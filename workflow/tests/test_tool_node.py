"""ToolNode 单元测试。"""

from __future__ import annotations

import pytest
from langchain_core.tools import tool

from agent_engine.nodes.tool_node import ToolNode


@tool
def search(query: str) -> str:
    """搜索 query 并返回结果。"""
    return f"结果: {query}"


@tool
def add(a: int, b: int) -> int:
    """计算 a + b。"""
    return a + b


@tool
def no_args_tool() -> str:
    """无参数工具。"""
    return "no_args_result"


class TestToolNode:
    """ToolNode 行为测试。"""

    def test_simple_tool_invocation(self) -> None:
        """简单工具调用：从 state 读 input，写入 tool_result。"""
        node = ToolNode(tool=search, input_key="query", output_key="search_result")
        result = node({"query": "LangGraph"})
        assert result["search_result"] == "结果: LangGraph"
        assert result["query"] == "LangGraph"  # 原 state 保留

    def test_default_keys(self) -> None:
        """默认 key 为 input/tool_result。"""
        node = ToolNode(tool=search)
        result = node({"input": "test"})
        assert result["tool_result"] == "结果: test"

    def test_multi_arg_tool_via_dict_input(self) -> None:
        """多参数工具：通过 dict 传入参数。"""
        node = ToolNode(tool=add, input_key="numbers", output_key="sum")
        result = node({"numbers": {"a": 3, "b": 5}})
        assert result["sum"] == 8

    def test_no_args_tool(self) -> None:
        """无参数工具：传空 dict 即可。"""
        node = ToolNode(tool=no_args_tool, input_key="input", output_key="output")
        result = node({"input": {}})
        assert result["output"] == "no_args_result"

    def test_missing_input_key_raises(self) -> None:
        """state 缺少 input_key 时抛 KeyError（明确错误）。"""
        node = ToolNode(tool=search, input_key="query", output_key="result")
        with pytest.raises(KeyError, match="'query'"):
            node({"other_key": "value"})

    def test_state_preservation(self) -> None:
        """state 中其他键被保留。"""
        node = ToolNode(tool=search, input_key="query", output_key="result")
        state = {
            "query": "test",
            "user_id": "alice",
            "context": {"key": "value"},
        }
        result = node(state)
        assert result["user_id"] == "alice"
        assert result["context"] == {"key": "value"}
        assert result["result"] == "结果: test"

    def test_to_runnable_compatible_with_langgraph(self) -> None:
        """to_runnable() 返回的 Runnable 可被 LangGraph 调用。"""
        from langchain_core.runnables import RunnableLambda

        node = ToolNode(tool=search, input_key="q", output_key="r")
        runnable = node.to_runnable()
        assert isinstance(runnable, RunnableLambda)
        result = runnable.invoke({"q": "hello"})
        assert result["r"] == "结果: hello"

    def test_repr_includes_tool_name(self) -> None:
        """__repr__ 输出便于调试。"""
        node = ToolNode(tool=search, input_key="q", output_key="r")
        r = repr(node)
        assert "ToolNode" in r
        assert "search" in r
