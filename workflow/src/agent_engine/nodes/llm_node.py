"""LLM 节点：基于 LangChain ChatModel 封装大语言模型调用。

设计要点：
    - 依赖倒置：接受 langchain_core 的 ``BaseChatModel`` 实例，不硬绑特定 LLM 厂商。
    - 测试友好：配合 ``FakeListChatModel`` 可零成本跑单元测试。
    - 生产可用：可注入 ``ChatOpenAI``（OpenCode 接入 Mimo v2.5）等真实模型。
"""

from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from agent_engine.nodes.base import NodeAdapter


class LLMNode(NodeAdapter):
    """LLM 调用节点。

    使用示例::

        from langchain_core.language_models.fake_chat_models import FakeListChatModel
        node = LLMNode(
            prompt_template="回答问题: {question}",
            llm=FakeListChatModel(responses=["这是答案"]),
            output_key="answer",
        )
        result = node({"question": "什么是 LangGraph?"})
        # result == {"question": "...", "answer": "这是答案"}
    """

    def __init__(
        self,
        prompt_template: str,
        llm: BaseChatModel,
        output_key: str = "response",
    ) -> None:
        """初始化 LLM 节点。

        Args:
            prompt_template: ChatPromptTemplate 模板字符串，使用 ``{var_name}`` 占位。
            llm: LangChain ``BaseChatModel`` 实例（如 ``ChatOpenAI`` / ``FakeListChatModel``）。
            output_key: LLM 输出在 state 中的键名，默认 ``response``。
        """
        self.prompt = ChatPromptTemplate.from_template(prompt_template)
        self.llm = llm
        self.output_key = output_key

    def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """执行 LLM 调用并将结果写入 state。

        Args:
            state: 工作流当前状态，需包含 prompt 模板所需的所有变量。

        Returns:
            包含 ``output_key`` 的更新 state。
        """
        messages = self.prompt.invoke(state)
        ai_message = self.llm.invoke(messages)
        # AIMessage.content 可能是 str 或 list，强制转为 str 写入 state
        content = ai_message.content
        if isinstance(content, list):
            # 处理 LangChain 1.x 的 content blocks（list[dict]）
            content = "".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            )
        return {**state, self.output_key: content}

    def __repr__(self) -> str:
        """可读字符串表示，便于日志与调试。"""
        return f"LLMNode(output_key={self.output_key!r}, llm={self.llm.__class__.__name__})"


__all__ = ["LLMNode"]
