"""WorkflowEngine 边与条件边的注册校验测试。"""

from __future__ import annotations

import pytest
from langgraph.graph import END, START

from agent_engine import EdgeError, NodeNotFoundError, WorkflowEngine


def _make_engine() -> WorkflowEngine:
    """构造包含 a/b/c 三个节点的引擎。"""
    engine = WorkflowEngine()
    engine.add_node("a", lambda s: s)
    engine.add_node("b", lambda s: s)
    engine.add_node("c", lambda s: s)
    return engine


class TestEdgeRegistration:
    """普通边注册测试。"""

    def test_add_edge_between_nodes(self) -> None:
        """可在两节点间添加边。"""
        engine = _make_engine()
        result = engine.add_edge("a", "b")
        assert result is engine

    def test_add_edge_from_start(self) -> None:
        """可从 START 添加边到节点。"""
        engine = _make_engine()
        engine.add_edge(START, "a")  # 不应抛错

    def test_add_edge_to_end(self) -> None:
        """可从节点添加边到 END。"""
        engine = _make_engine()
        engine.add_edge("a", END)  # 不应抛错

    def test_edge_to_unregistered_node_raises(self) -> None:
        """指向未注册节点的边应抛 NodeNotFoundError。"""
        engine = _make_engine()
        with pytest.raises(NodeNotFoundError, match="'missing' 未注册"):
            engine.add_edge("a", "missing")

    def test_edge_from_unregistered_node_raises(self) -> None:
        """从未注册节点出发的边应抛 NodeNotFoundError。"""
        engine = _make_engine()
        with pytest.raises(NodeNotFoundError, match="'missing' 未注册"):
            engine.add_edge("missing", "a")


class TestConditionalEdges:
    """条件边注册测试。"""

    def test_add_conditional_edge(self) -> None:
        """可注册简单条件边。"""
        engine = _make_engine()
        engine.add_conditional_edges("a", lambda s: "b")
        # 不会抛错

    def test_add_conditional_edge_with_path_map(self) -> None:
        """带 path_map 的条件边。"""
        engine = _make_engine()
        engine.add_conditional_edges(
            "a",
            lambda s: "go_b",
            path_map={"go_b": "b", "go_c": "c"},
        )

    def test_conditional_edge_invalid_path_func(self) -> None:
        """path 必须为可调用对象。"""
        engine = _make_engine()
        with pytest.raises(ValueError, match="可调用对象"):
            engine.add_conditional_edges("a", "not callable")  # type: ignore[arg-type]

    def test_conditional_edge_path_map_unregistered(self) -> None:
        """path_map 指向未注册节点应抛错。"""
        engine = _make_engine()
        with pytest.raises(NodeNotFoundError, match="'missing'"):
            engine.add_conditional_edges(
                "a",
                lambda s: "go",
                path_map={"go": "missing"},
            )

    def test_conditional_edge_allows_end_target(self) -> None:
        """path_map 中可使用 END 作为目标。"""
        engine = _make_engine()
        engine.add_conditional_edges(
            "a",
            lambda s: "stop",
            path_map={"stop": END},
        )


class TestEntryAndFinish:
    """入口/出口节点测试。"""

    def test_set_entry_point(self) -> None:
        """可设置入口节点。"""
        engine = _make_engine()
        engine.set_entry_point("a")
        # 不会抛错

    def test_set_entry_unregistered_raises(self) -> None:
        """入口节点未注册应抛 NodeNotFoundError。"""
        engine = _make_engine()
        with pytest.raises(NodeNotFoundError):
            engine.set_entry_point("missing")

    def test_set_finish_point(self) -> None:
        """可设置结束节点。"""
        engine = _make_engine()
        engine.set_finish_point("c")

    def test_compile_requires_entry_point(self) -> None:
        """未设置入口时编译应抛 EdgeError。"""
        engine = _make_engine()
        engine.set_finish_point("c")
        with pytest.raises(EdgeError, match="入口节点"):
            engine.compile()

    def test_compile_without_finish_point_ok_when_conditional_to_end(self) -> None:
        """未显式设置结束节点但有条件边到 END 时，编译可成功。"""
        engine = _make_engine()
        engine.add_conditional_edges(
            "a",
            lambda s: END,
        )
        engine.set_entry_point("a")
        # 不调用 set_finish_point，编译应通过
        engine.compile()  # 不抛错即通过

    def test_compile_without_set_entry_point_message(self) -> None:
        """未设置入口时编译错误的提示应同时提到两种入口表达方式。"""
        engine = _make_engine()
        engine.set_finish_point("a")
        with pytest.raises(EdgeError) as exc_info:
            engine.compile()
        # 错误信息应同时提示 set_entry_point 和 add_edge(START, ...) 两种入口设置方式
        msg = str(exc_info.value)
        assert "set_entry_point" in msg
        assert "add_edge(START" in msg

    def test_add_edge_from_start_is_equivalent_to_set_entry_point(self) -> None:
        """add_edge(START, "a") 等价于 set_entry_point("a")，会自动设置 _entry_point。"""
        engine = _make_engine()
        engine.add_edge(START, "a")
        # 不显式调用 set_entry_point，编译应能识别入口
        engine.compile()  # 不抛错即通过

    def test_set_entry_point_after_add_edge_from_start_same_target_ok(self) -> None:
        """先 add_edge(START, "a") 后 set_entry_point("a") 不报错（一致）。"""
        engine = _make_engine()
        engine.add_edge(START, "a")
        engine.set_entry_point("a")  # 一致，不抛错

    def test_set_entry_point_after_add_edge_from_start_conflict_raises(self) -> None:
        """先 add_edge(START, "a") 后 set_entry_point("b") 应抛 EdgeError。"""
        engine = _make_engine()
        engine.add_edge(START, "a")
        with pytest.raises(EdgeError, match="入口已设置为"):
            engine.set_entry_point("b")

    def test_add_edge_from_start_after_set_entry_point_conflict_raises(self) -> None:
        """先 set_entry_point("a") 后 add_edge(START, "b") 应抛 EdgeError。"""
        engine = _make_engine()
        engine.set_entry_point("a")
        with pytest.raises(EdgeError, match="入口已设置"):
            engine.add_edge(START, "b")

    def test_add_edge_from_start_after_set_entry_point_same_target_ok(self) -> None:
        """先 set_entry_point("a") 后 add_edge(START, "a") 不报错（idempotent）。"""
        engine = _make_engine()
        engine.set_entry_point("a")
        engine.add_edge(START, "a")  # 同名，不抛错
        engine.compile()  # 编译应成功
