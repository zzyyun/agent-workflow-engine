"""Tool 节点：基于 LangChain Tool 协议封装函数/HTTP 调用。"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import BaseTool

from agent_engine.nodes.base import NodeAdapter


class ToolNode(NodeAdapter):
    """工具调用节点。

    使用示例::

        from langchain_core.tools import tool

        @tool
        def search(query: str) -> str:
            \"\"\"搜索 query 并返回结果。\"\"\"
            return f"结果: {query}"

        node = ToolNode(tool=search, input_key="query", output_key="search_result")
        result = node({"query": "LangGraph"})
        # result == {"query": "LangGraph", "search_result": "结果: LangGraph"}
    """

    def __init__(
        self,
        tool: BaseTool,
        input_key: str = "input",
        output_key: str = "tool_result",
    ) -> None:
        """初始化 Tool 节点。

        Args:
            tool: LangChain ``BaseTool`` 实例（用 ``@tool`` 装饰器创建）。
            input_key: 从 state 中读取的输入键名。
            output_key: 工具结果在 state 中的输出键名。
        """
        self.tool = tool
        self.input_key = input_key
        self.output_key = output_key

    def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """调用工具并将结果写入 state。

        Args:
            state: 工作流当前状态，需包含 ``input_key`` 指定的输入。

        Returns:
            包含 ``output_key`` 的更新 state。

        Raises:
            KeyError: state 中缺少 ``input_key``。
        """
        if self.input_key not in state:
            raise KeyError(
                f"ToolNode 需要 state['{self.input_key}']，但 state 中缺少该键。"
                f"现有 keys: {list(state.keys())}"
            )
        result = self.tool.invoke(state[self.input_key])
        return {**state, self.output_key: result}

    def __repr__(self) -> str:
        """可读字符串表示。"""
        return (
            f"ToolNode(tool={self.tool.name!r}, "
            f"input_key={self.input_key!r}, output_key={self.output_key!r})"
        )


__all__ = ["ToolNode"]
