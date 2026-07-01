"""LLM Provider 注册表。

设计目标：
    1. 依赖反转：``DSL`` 与 ``builder`` 不硬绑特定 LLM 厂商，通过 provider 名字
       懒加载对应实现。基线仅依赖 ``langchain-core``，无需安装 OpenAI/Anthropic SDK。
    2. 内置 provider：
       - ``fake``：``FakeListChatModel``，零依赖，供 demo 与单元测试使用（默认）。
       - ``openai``：``langchain_openai.ChatOpenAI``（需安装 ``langchain-openai``）。
       - ``anthropic``：``langchain_anthropic.ChatAnthropic``（需安装拓展包）。
    3. 可扩展：通过 ``register_provider(name, factory)`` 注册自定义 provider，
       factory 接收 ``params`` dict 返回 ``BaseChatModel`` 实例。
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.language_models.fake_chat_models import FakeListChatModel


class ProviderError(ValueError):
    """LLM provider 加载失败（未知名称、缺包、参数非法等）。"""


# 全局注册表：provider_name -> factory(params) -> BaseChatModel
# factory 在调用时才懒加载具体厂商包，避免基线引入额外依赖。
_PROVIDERS: dict[str, Callable[[dict[str, Any]], BaseChatModel]] = {}


def register_provider(name: str, factory: Callable[[dict[str, Any]], BaseChatModel]) -> None:
    """注册一个 LLM provider 工厂。

    Args:
        name: provider 短名（如 ``"fake"`` / ``"openai"``）。
        factory: 接收 ``params`` dict，返回 ``BaseChatModel`` 实例的工厂函数。
    """
    if not name or not isinstance(name, str):
        raise ValueError(f"provider 名称必须为非空字符串，实际值: {name!r}")
    if not callable(factory):
        raise TypeError(f"provider {name!r} 的 factory 必须可调用")
    _PROVIDERS[name] = factory


def _fake_factory(params: dict[str, Any]) -> BaseChatModel:
    """fake provider：``FakeListChatModel``，零依赖。"""
    responses = params.get("responses", [])
    if not isinstance(responses, list):
        raise ProviderError(
            f"fake provider 的 'responses' 必须是列表，实际类型: {type(responses).__name__}"
        )
    # 透传其他可选参数（如 model_name），方便测试。
    return FakeListChatModel(responses=list(responses))


def _openai_factory(params: dict[str, Any]) -> BaseChatModel:
    """openai provider：懒加载 ``langchain_openai.ChatOpenAI``。"""
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as e:  # 依赖未安装
        raise ProviderError(
            "使用 openai provider 需安装 langchain-openai：pip install langchain-openai"
        ) from e
    # 排除本注册表专用字段，避免污染 ChatOpenAI 的构造参数
    ctor_params = {k: v for k, v in params.items() if k not in {"provider", "responses"}}
    return ChatOpenAI(**ctor_params)


def _anthropic_factory(params: dict[str, Any]) -> BaseChatModel:
    """anthropic provider：懒加载 ``langchain_anthropic.ChatAnthropic``。"""
    try:
        from langchain_anthropic import ChatAnthropic
    except ImportError as e:
        raise ProviderError(
            "使用 anthropic provider 需安装 langchain-anthropic：pip install langchain-anthropic"
        ) from e
    ctor_params = {k: v for k, v in params.items() if k not in {"provider", "responses"}}
    return ChatAnthropic(**ctor_params)


def get_llm(provider: str, params: dict[str, Any]) -> BaseChatModel:
    """根据 provider 名字与参数构造 ``BaseChatModel`` 实例。

    Args:
        provider: 注册的 provider 名字（默认场景下用 ``"fake"``）。
        params: 来自 DSL 节点 ``params`` 的参数字典。

    Returns:
        ``BaseChatModel`` 实例。

    Raises:
        ProviderError: provider 未注册或其工厂抛错（缺包/参数非法）。
    """
    if not provider or not isinstance(provider, str):
        raise ProviderError(f"provider 名称必须为非空字符串，实际值: {provider!r}")
    factory = _PROVIDERS.get(provider)
    if factory is None:
        known = ", ".join(sorted(_PROVIDERS)) or "(无)"
        raise ProviderError(
            f"未知的 LLM provider {provider!r}，已注册: {known}。可通过 register_provider() 扩展。"
        )
    try:
        return factory(params)
    except ProviderError:
        raise
    except Exception as e:  # 包装厂商包抛出的参数/导入错误
        raise ProviderError(f"provider {provider!r} 实例化失败: {type(e).__name__}: {e}") from e


# 注册内置 provider（导入本模块即生效）
register_provider("fake", _fake_factory)
register_provider("openai", _openai_factory)
register_provider("anthropic", _anthropic_factory)


__all__ = ["ProviderError", "get_llm", "register_provider"]
