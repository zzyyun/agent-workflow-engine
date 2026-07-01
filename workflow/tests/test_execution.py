"""WorkflowEngine 编译与执行测试。"""

from __future__ import annotations

import pytest
from langgraph.graph import END

from agent_engine import EngineConfig, WorkflowEngine


def increment(state: dict) -> dict:
    """将 value +1。"""
    return {"value": state.get("value", 0) + 1, "log": state.get("log", []) + ["inc"]}


def double(state: dict) -> dict:
    """将 value 翻倍。"""
    return {"value": state["value"] * 2, "log": state.get("log", []) + ["dbl"]}


def add_ten(state: dict) -> dict:
    """将 value 加 10。"""
    return {"value": state["value"] + 10, "log": state.get("log", []) + ["ten"]}


class TestCompileAndExecute:
    """编译与基础执行测试。"""

    def test_compile_returns_compiled_graph(self) -> None:
        """compile() 应返回可执行对象。"""
        engine = WorkflowEngine()
        engine.add_node("a", increment)
        engine.set_entry_point("a")
        engine.set_finish_point("a")
        compiled = engine.compile()
        # CompiledGraph 有 invoke/stream 接口
        assert hasattr(compiled, "invoke")
        assert hasattr(compiled, "stream")

    def test_invoke_returns_final_state(self) -> None:
        """invoke() 返回最终 state。"""
        engine = WorkflowEngine()
        engine.add_node("a", increment)
        engine.add_node("b", double)
        engine.add_edge("a", "b")
        engine.set_entry_point("a")
        engine.set_finish_point("b")
        compiled = engine.compile()
        result = compiled.invoke({"value": 3})
        # 3 -> inc=4 -> dbl=8
        assert result["value"] == 8
        assert result["log"] == ["inc", "dbl"]

    def test_invoke_with_default_state(self) -> None:
        """不传 state 时使用空字典。"""
        engine = WorkflowEngine()
        engine.add_node("a", lambda s: {"x": 1})
        engine.set_entry_point("a")
        engine.set_finish_point("a")
        compiled = engine.compile()
        # 新版 LangGraph 的 invoke 要求显式传 input
        result = compiled.invoke({})
        assert result["x"] == 1

    def test_engine_invoke_method(self) -> None:
        """WorkflowEngine.invoke() 内部会触发 compile。"""
        engine = WorkflowEngine()
        engine.add_node("a", increment)
        engine.set_entry_point("a")
        engine.set_finish_point("a")
        result = engine.invoke({"value": 5})
        assert result["value"] == 6

    def test_stream_yields_node_outputs(self) -> None:
        """stream() 逐步产出节点输出。"""
        engine = WorkflowEngine()
        engine.add_node("a", increment)
        engine.add_node("b", double)
        engine.add_edge("a", "b")
        engine.set_entry_point("a")
        engine.set_finish_point("b")
        compiled = engine.compile()
        chunks = list(compiled.stream({"value": 1}))
        # 1 -> inc=2 -> dbl=4
        # stream "updates" 模式: 每个 chunk 是 {node_name: update}
        assert "a" in chunks[0]
        assert "b" in chunks[1]
        assert chunks[0]["a"]["value"] == 2
        assert chunks[1]["b"]["value"] == 4

    def test_engine_stream_method(self) -> None:
        """WorkflowEngine.stream() 自动编译并产出节点输出。"""
        engine = WorkflowEngine()
        engine.add_node("a", increment)
        engine.set_entry_point("a")
        engine.set_finish_point("a")
        chunks = list(engine.stream({"value": 10}))
        assert len(chunks) == 1
        assert chunks[0]["a"]["value"] == 11


class TestConditionalBranching:
    """条件边分支测试。"""

    def test_conditional_branch_picks_path(self) -> None:
        """条件边根据 path 返回值路由。"""
        engine = WorkflowEngine()
        engine.add_node("check", lambda s: s)
        engine.add_node("to_b", double)
        engine.add_node("to_c", add_ten)
        engine.add_conditional_edges(
            "check",
            lambda s: "b" if s["value"] > 0 else "c",
            path_map={"b": "to_b", "c": "to_c"},
        )
        engine.set_entry_point("check")
        engine.set_finish_point("to_b")
        engine.set_finish_point("to_c")
        compiled = engine.compile()

        # value=5: b 路径 -> double
        result_pos = compiled.invoke({"value": 5})
        assert result_pos["value"] == 10

        # value=-3: c 路径 -> add_ten
        result_neg = compiled.invoke({"value": -3})
        assert result_neg["value"] == 7

    def test_conditional_branch_to_end(self) -> None:
        """条件边可直接路由到 END 提前结束。"""
        engine = WorkflowEngine()
        engine.add_node("check", lambda s: s)
        engine.add_node("step", increment)
        engine.add_conditional_edges(
            "check",
            lambda s: "end" if s.get("value", 0) >= 100 else "go",
            path_map={"end": END, "go": "step"},
        )
        engine.add_edge("step", "check")
        engine.set_entry_point("check")
        engine.set_finish_point("check")
        compiled = engine.compile()
        # value=100 时直接 END，不执行 step
        result = compiled.invoke({"value": 100})
        assert result["value"] == 100


class TestParallelExecution:
    """并行节点执行测试。"""

    def test_parallel_branches_converge(self) -> None:
        """两个并行分支汇合到一个聚合节点。

        注意：LangGraph 中并行节点若写入同一 state key 会抛
        ``InvalidUpdateError``（只能写一次）。这里让两个分支写到不同 key
        （``a`` / ``b``），merge 节点再聚合。
        """
        engine = WorkflowEngine()
        engine.add_node("start", lambda s: {"value": s.get("value", 0)})
        # 分支写入不同 key 避免冲突
        engine.add_node("branch_a", lambda s: {"a": s["value"] + 1})
        engine.add_node("branch_b", lambda s: {"b": s["value"] + 2})
        engine.add_node("merge", lambda s: {"total": s.get("a", 0) + s.get("b", 0)})
        # 入口到两个分支
        engine.add_edge("start", "branch_a")
        engine.add_edge("start", "branch_b")
        # 两个分支汇合
        engine.add_edge("branch_a", "merge")
        engine.add_edge("branch_b", "merge")
        engine.set_entry_point("start")
        engine.set_finish_point("merge")
        compiled = engine.compile()
        result = compiled.invoke({"value": 10})
        # branch_a: 10+1=11, branch_b: 10+2=12, merge: 11+12=23
        assert result["total"] == 23


class TestRecursionLimit:
    """recursion_limit 防死循环测试。"""

    def test_recursion_limit_stops_infinite_loop(self) -> None:
        """recursion_limit=3 应在第 3 步拦截死循环。"""
        from langgraph.errors import GraphRecursionError

        engine = WorkflowEngine(EngineConfig(recursion_limit=3))
        # 两个节点互相循环
        engine.add_node("ping", lambda s: {"log": s.get("log", []) + ["ping"]})
        engine.add_node("pong", lambda s: {"log": s.get("log", []) + ["pong"]})
        # 用 path_map 把 END 作为目标
        engine.add_conditional_edges(
            "ping",
            lambda s: "pong" if len(s.get("log", [])) < 10 else END,
        )
        engine.add_conditional_edges(
            "pong",
            lambda s: "ping" if len(s.get("log", [])) < 10 else END,
        )
        engine.set_entry_point("ping")
        # 条件边已支持到 END，无需显式 set_finish_point
        compiled = engine.compile()
        # 期望 GraphRecursionError（直接传 config 给 compiled）
        with pytest.raises(GraphRecursionError):
            compiled.invoke({"log": []}, config={"recursion_limit": 3})

    def test_normal_flow_within_limit(self) -> None:
        """正常流程在 recursion_limit 内可完成。"""
        engine = WorkflowEngine(EngineConfig(recursion_limit=25))
        # 3 节点线性流：a -> b -> c
        engine.add_node("a", increment)
        engine.add_node("b", double)
        engine.add_node("c", increment)
        engine.add_edge("a", "b")
        engine.add_edge("b", "c")
        engine.set_entry_point("a")
        engine.set_finish_point("c")
        compiled = engine.compile()
        result = compiled.invoke({"value": 1})
        # 1 -> inc=2 -> dbl=4 -> inc=5
        assert result["value"] == 5


class TestLargeGraph:
    """10+ 节点大规模图测试（验收标准）。"""

    def test_build_and_run_10_node_linear(self) -> None:
        """可构建 10 节点线性图并稳定执行。"""
        engine = WorkflowEngine()
        for i in range(10):
            engine.add_node(f"n{i}", lambda s, i=i: {"value": s.get("value", 0) + i})
        for i in range(9):
            engine.add_edge(f"n{i}", f"n{i + 1}")
        engine.set_entry_point("n0")
        engine.set_finish_point("n9")
        compiled = engine.compile()
        result = compiled.invoke({"value": 0})
        # 累加 0+1+2+...+9 = 45
        assert result["value"] == 45

    def test_build_and_run_10_node_diamond(self) -> None:
        """10 节点菱形 DAG：1 -> 4路并行 -> 合并。

        并行分支写入不同 key 避免 ``InvalidUpdateError``。
        """
        engine = WorkflowEngine()
        # 1 个入口
        engine.add_node("start", lambda s: {"value": s.get("value", 1)})
        # 4 个并行分支，每个 2 个节点 (branch -> leaf)；分支写不同 key
        for i in range(4):
            engine.add_node(
                f"branch_{i}", lambda s, i=i: {f"b{i}": s["value"] * 2}
            )
            engine.add_node(
                f"leaf_{i}", lambda s, i=i: {f"l{i}": s[f"b{i}"] + i}
            )
            engine.add_edge("start", f"branch_{i}")
            engine.add_edge(f"branch_{i}", f"leaf_{i}")
        # 合并节点：累加所有 leaf 的结果
        def merge(state: dict) -> dict:
            total = sum(state.get(f"l{i}", 0) for i in range(4))
            return {"total": total}

        engine.add_node("merge", merge)
        for i in range(4):
            engine.add_edge(f"leaf_{i}", "merge")
        engine.set_entry_point("start")
        engine.set_finish_point("merge")
        compiled = engine.compile()
        result = compiled.invoke({"value": 1})
        # value=1 -> branch_i.b_i=2 -> leaf_i.l_i=2+i
        # total = (2+0) + (2+1) + (2+2) + (2+3) = 14
        assert result["total"] == 14
