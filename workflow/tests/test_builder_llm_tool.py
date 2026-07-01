"""builder 对 llm / tool 节点的构造测试（CLI 可用化）。"""

from __future__ import annotations

import pytest
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.tools import tool

from agent_engine.dsl.builder import BuilderError, build_engine
from agent_engine.dsl.models import NodeSpec, WorkflowDSL
from agent_engine.nodes import LLMNode, ToolNode

# ------------------------------------------------------------------ #
# fixtures：作为 import ref 引用目标的示例对象
# ------------------------------------------------------------------ #


@tool
def echo_tool(text: str) -> str:
    """回显 text。"""
    return text


def _fake_llm_factory(params: dict) -> FakeListChatModel:
    """作为 ``params.llm`` 工厂引用的示例。"""
    return FakeListChatModel(responses=list(params.get("responses", ["ok"])))


# 让 builder 通过 module:path 找到上述对象
_FAKE_MODULE = "tests.test_builder_llm_tool"


def _make_dsl(nodes: list[NodeSpec], entry: str, finish: list[str] | None = None) -> WorkflowDSL:
    return WorkflowDSL(name="t", nodes=nodes, entry=entry, finish=finish or [])


# ------------------------------------------------------------------ #
# llm 节点
# ------------------------------------------------------------------ #


class TestBuildLLMNode:
    """llm 节点构造。"""

    def test_llm_via_fake_provider(self) -> None:
        """provider=fake + responses 构造 LLMNode，invoke 得预期输出。"""
        node = NodeSpec(
            id="g",
            type="llm",
            params={
                "provider": "fake",
                "responses": ["42"],
                "prompt_template": "Q: {q}",
                "output_key": "answer",
            },
        )
        dsl = _make_dsl([node], entry="g", finish=["g"])

        # 直接取出 action 验证类型与行为（build_engine 已注册节点）
        engine = build_engine(dsl)
        result = engine.invoke({"q": "x"})
        assert result["answer"] == "42"
        assert result["q"] == "x"
        # 确认动作是 LLMNode 实例
        assert isinstance(engine._nodes["g"], LLMNode)

    def test_llm_via_import_ref_instance(self) -> None:
        """params.llm 引用模块属性（已是 BaseChatModel 实例）。"""
        node = NodeSpec(
            id="g",
            type="llm",
            params={
                "llm": "langchain_core.language_models.fake_chat_models:FakeListChatModel",
                "prompt_template": "hi",
                "output_key": "out",
                # 注意：此处 ref 解析到的是类本身（callable），会以 params 调用
                "responses": ["hi-back"],
            },
        )
        dsl = _make_dsl([node], entry="g", finish=["g"])
        engine = build_engine(dsl)
        assert engine.invoke({})["out"] == "hi-back"

    def test_llm_missing_prompt_template_raises(self) -> None:
        """缺 prompt_template 应 BuilderError。"""
        node = NodeSpec(
            id="g",
            type="llm",
            params={"provider": "fake", "responses": ["x"]},
        )
        with pytest.raises(BuilderError, match="prompt_template"):
            build_engine(_make_dsl([node], entry="g", finish=["g"]))

    def test_llm_unknown_provider_raises(self) -> None:
        """未知 provider 应 BuilderError（包装 ProviderError）。"""
        node = NodeSpec(
            id="g",
            type="llm",
            params={"provider": "nope", "prompt_template": "hi"},
        )
        with pytest.raises(BuilderError, match="provider"):
            build_engine(_make_dsl([node], entry="g", finish=["g"]))


# ------------------------------------------------------------------ #
# tool 节点
# ------------------------------------------------------------------ #


class TestBuildToolNode:
    """tool 节点构造。"""

    def test_tool_via_import_ref(self) -> None:
        """params.tool 引用 @tool 对象，构造 ToolNode。"""
        node = NodeSpec(
            id="t",
            type="tool",
            params={
                "tool": f"{_FAKE_MODULE}:echo_tool",
                "input_key": "text",
                "output_key": "echoed",
            },
        )
        dsl = _make_dsl([node], entry="t", finish=["t"])
        engine = build_engine(dsl)
        result = engine.invoke({"text": "hello"})
        assert result["echoed"] == "hello"
        assert isinstance(engine._nodes["t"], ToolNode)

    def test_tool_default_keys(self) -> None:
        """缺 input_key/output_key 时用默认 input/tool_result。"""
        node = NodeSpec(
            id="t",
            type="tool",
            params={"tool": f"{_FAKE_MODULE}:echo_tool"},
        )
        dsl = _make_dsl([node], entry="t", finish=["t"])
        engine = build_engine(dsl)
        assert engine.invoke({"input": "yo"})["tool_result"] == "yo"

    def test_tool_missing_ref_raises(self) -> None:
        """缺 params.tool 应 BuilderError。"""
        node = NodeSpec(id="t", type="tool", params={})
        with pytest.raises(BuilderError, match="params.tool"):
            build_engine(_make_dsl([node], entry="t", finish=["t"]))

    def test_tool_bad_ref_raises(self) -> None:
        """params.tool 指向不存在的属性应 BuilderError。"""
        node = NodeSpec(
            id="t",
            type="tool",
            params={"tool": f"{_FAKE_MODULE}:no_such_tool"},
        )
        with pytest.raises(BuilderError):
            build_engine(_make_dsl([node], entry="t", finish=["t"]))


# ------------------------------------------------------------------ #
# 集成：llm → tool 链
# ------------------------------------------------------------------ #


class TestLLMToolChain:
    """LLM 输出喂给 Tool。"""

    def test_llm_then_tool_chain(self) -> None:
        """fake LLM 产出 '10'，tool add_one 得 11。"""
        nodes = [
            NodeSpec(
                id="gen",
                type="llm",
                params={
                    "provider": "fake",
                    "responses": ["10"],
                    "prompt_template": "num {hint}",
                    "output_key": "num_str",
                },
            ),
            NodeSpec(
                id="add",
                type="tool",
                depends_on=["gen"],
                params={
                    "tool": "examples.demo_nodes:add_one",
                    "input_key": "num_str",
                    "output_key": "result",
                },
            ),
        ]
        dsl = _make_dsl(nodes, entry="gen", finish=["add"])
        engine = build_engine(dsl)
        result = engine.invoke({"hint": "any"})
        assert result["num_str"] == "10"
        assert result["result"] == 11
