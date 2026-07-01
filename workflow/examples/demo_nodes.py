"""Phase 1.4 端到端 demo 使用的节点函数。

提供给 ``examples/cli_demo.yaml`` 中的 passthrough 节点引用，
以及 ``examples/llm_tool_demo.yaml`` 中的 tool 节点与 LLM 工厂引用。
"""

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.tools import tool


def increment(state: dict) -> dict:
    """将 value 加 1。"""
    return {"value": state.get("value", 0) + 1, "log": state.get("log", []) + ["inc"]}


def double(state: dict) -> dict:
    """将 value 翻倍。"""
    return {"value": state["value"] * 2, "log": state.get("log", []) + ["dbl"]}


@tool
def add_one(text: str) -> int:
    """把 text 解析为整数并加 1（用于 LLM → Tool 链 demo）。"""
    return int(text) + 1


@tool
def upper(text: str) -> str:
    """把 text 转为大写（用于 Tool 节点 demo）。"""
    return text.upper()


def fake_llm(**kwargs):
    """LLM 工厂：返回一个固定回答的 FakeListChatModel。

    供 ``params.llm`` 引用为工厂：``examples.demo_nodes:fake_llm``。
    支持 ``builder`` 的两种调用约定（接收 kwargs 或 params dict）。
    固定响应 ``"10"``，配合 ``add_one`` 得到 result 11。
    """
    # builder 倾向于用 **params 调用；兼容直接传 params dict 的旧用法
    p = kwargs.get("params") if isinstance(kwargs.get("params"), dict) else kwargs
    responses = p.get("responses", ["10"])
    return FakeListChatModel(responses=list(responses))
