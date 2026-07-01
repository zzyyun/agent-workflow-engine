"""LLMNode 单元测试。"""

from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage

from agent_engine.nodes.llm_node import LLMNode


class TestLLMNode:
    """LLMNode 行为测试。"""

    def test_simple_prompt_invokes_llm(self) -> None:
        """简单 prompt 模板：变量被替换，LLM 响应写入 output_key。"""
        llm = FakeListChatModel(responses=["回答是 42"])
        node = LLMNode(
            prompt_template="问题: {question}",
            llm=llm,
            output_key="answer",
        )
        result = node({"question": "生命的意义"})
        assert result["answer"] == "回答是 42"
        assert result["question"] == "生命的意义"  # 原 state 保留

    def test_default_output_key(self) -> None:
        """未指定 output_key 时使用默认值 'response'。"""
        llm = FakeListChatModel(responses=["hi"])
        node = LLMNode(prompt_template="say hi", llm=llm)
        result = node({})
        assert result["response"] == "hi"
        assert "answer" not in result  # 默认 key 是 response，不是 answer

    def test_multiple_template_variables(self) -> None:
        """多变量模板：所有变量从 state 中读取。"""
        llm = FakeListChatModel(responses=["综合回答"])
        node = LLMNode(
            prompt_template="基于 {context}，回答 {question}",
            llm=llm,
            output_key="answer",
        )
        result = node({"context": "LangGraph 是图执行框架", "question": "什么是 DAG?"})
        assert result["answer"] == "综合回答"
        assert result["context"] == "LangGraph 是图执行框架"
        assert result["question"] == "什么是 DAG?"

    def test_llm_called_with_messages(self) -> None:
        """LLM 接收的应是格式化后的消息列表而非原始模板。"""
        captured: list[list] = []

        class CapturingLLM(FakeListChatModel):
            def invoke(self, input_, **kwargs):  # type: ignore[override]
                captured.append(input_)
                return AIMessage(content="captured")

        node = LLMNode(
            prompt_template="Echo: {msg}",
            llm=CapturingLLM(responses=[]),
            output_key="out",
        )
        node({"msg": "hello"})
        assert len(captured) == 1
        # input_ 是 ChatPromptValue 实例，需用 to_messages() 转为 list[BaseMessage]
        messages = captured[0].to_messages()
        assert len(messages) >= 1
        assert "Echo: hello" in messages[0].content

    def test_sequential_invocations_consume_responses(self) -> None:
        """多次调用按顺序消费 FakeListChatModel 的 responses 列表。"""
        llm = FakeListChatModel(responses=["first", "second", "third"])
        node = LLMNode(prompt_template="Q: {q}", llm=llm, output_key="a")
        assert node({"q": "1"})["a"] == "first"
        assert node({"q": "2"})["a"] == "second"
        assert node({"q": "3"})["a"] == "third"

    def test_to_runnable_compatible_with_langgraph(self) -> None:
        """to_runnable() 返回的 Runnable 可被 LangGraph 调用。"""
        from langchain_core.runnables import RunnableLambda

        llm = FakeListChatModel(responses=["ok"])
        node = LLMNode(prompt_template="hi", llm=llm, output_key="out")
        runnable = node.to_runnable()
        assert isinstance(runnable, RunnableLambda)
        result = runnable.invoke({})
        assert result["out"] == "ok"

    def test_repr_includes_class_names(self) -> None:
        """__repr__ 输出便于调试。"""
        llm = FakeListChatModel(responses=["x"])
        node = LLMNode(prompt_template="p", llm=llm, output_key="k")
        r = repr(node)
        assert "LLMNode" in r
        assert "FakeListChatModel" in r
        assert "'k'" in r
