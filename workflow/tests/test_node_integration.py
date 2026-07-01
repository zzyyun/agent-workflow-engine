"""LLM / Tool / Condition 三节点与 WorkflowEngine 集成测试。"""

from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.tools import tool

from agent_engine import WorkflowEngine
from agent_engine.nodes import ConditionNode, LLMNode, ToolNode


@tool
def parse_and_add_one(text: str) -> int:
    """将 text 解析为整数并加 1。"""
    return int(text) + 1


@tool
def to_upper(text: str) -> str:
    """将 text 转为大写。"""
    return text.upper()


@tool
def is_long_text(text: str) -> str:
    """返回文本长度信息（用于条件分支演示）。"""
    return f"length={len(text)}"


class TestLLMToolConditionIntegration:
    """三节点工作流集成：LLM → Tool → Condition 路由。"""

    def test_llm_then_tool_sequential(self) -> None:
        """LLM 节点输出作为 Tool 节点输入，串行执行。"""
        # LLM 生成 "10"，Tool 解析为 11
        llm = FakeListChatModel(responses=["10"])
        llm_node = LLMNode(
            prompt_template="只输出数字 {hint}",
            llm=llm,
            output_key="number_str",
        )
        tool_node = ToolNode(
            tool=parse_and_add_one, input_key="number_str", output_key="result"
        )

        engine = WorkflowEngine()
        engine.add_node("llm", llm_node)
        engine.add_node("tool", tool_node)
        engine.add_edge("llm", "tool")
        engine.set_entry_point("llm")
        engine.set_finish_point("tool")

        result = engine.invoke({"hint": "10"})
        assert result["number_str"] == "10"
        assert result["result"] == 11

    def test_condition_routes_to_different_tools(self) -> None:
        """Condition 节点根据 LLM 输出长度路由到不同 Tool 节点。"""
        # LLM 输出 "hello"（短文本）→ is_long_text 路径
        # LLM 输出 "very long text indeed"（长文本）→ 另一条路径
        llm = FakeListChatModel(responses=["hello"])  # 5 字符，走 short 分支
        llm_node = LLMNode(
            prompt_template="reply {q}",
            llm=llm,
            output_key="reply",
        )
        long_tool = ToolNode(
            tool=is_long_text, input_key="reply", output_key="length_info"
        )
        upper_tool = ToolNode(
            tool=to_upper, input_key="reply", output_key="uppered"
        )
        cond = ConditionNode(
            condition=lambda s: len(s["reply"]) > 8,
            true_branch="long",
            false_branch="short",
        )

        engine = WorkflowEngine()
        engine.add_node("llm", llm_node)
        engine.add_node("long_path", long_tool)
        engine.add_node("short_path", upper_tool)
        engine.add_conditional_edges(
            "llm",
            path=cond.evaluate,
            path_map={"long": "long_path", "short": "short_path"},
        )
        engine.set_entry_point("llm")
        engine.set_finish_point("long_path")
        engine.set_finish_point("short_path")

        result = engine.invoke({"q": "hi"})
        # "hello" 长度 5 <= 8，走 short_path (upper)
        assert result["uppered"] == "HELLO"

    def test_three_node_chain_invoke(self) -> None:
        """完整三节点链：LLM → Tool → Condition 决定下一步。"""
        llm = FakeListChatModel(responses=["hello world"])
        llm_node = LLMNode(
            prompt_template="say {what}",
            llm=llm,
            output_key="raw",
        )
        upper_node = ToolNode(
            tool=to_upper, input_key="raw", output_key="processed"
        )
        # 验证节点：检查 processed 是否真的大写
        def validate(state: dict) -> dict:
            return {**state, "validated": state.get("processed", "").isupper()}

        engine = WorkflowEngine()
        engine.add_node("llm", llm_node)
        engine.add_node("upper", upper_node)
        engine.add_node("validate", validate)
        engine.add_edge("llm", "upper")
        engine.add_edge("upper", "validate")
        engine.set_entry_point("llm")
        engine.set_finish_point("validate")  # validate 节点结束即终止

        result = engine.invoke({"what": "hello"})
        assert result["raw"] == "hello world"
        assert result["processed"] == "HELLO WORLD"
        assert result["validated"] is True

    def test_llm_node_to_runnable_in_engine(self) -> None:
        """LLMNode.to_runnable() 转换后的 Runnable 可被 WorkflowEngine 通过 duck typing 接受。"""
        runnable = LLMNode(
            prompt_template="hi",
            llm=FakeListChatModel(responses=["hi-back"]),
            output_key="greeting",
        ).to_runnable()

        engine = WorkflowEngine()
        engine.add_node("chat", runnable)
        engine.set_entry_point("chat")
        engine.set_finish_point("chat")

        result = engine.invoke({})
        assert result["greeting"] == "hi-back"
