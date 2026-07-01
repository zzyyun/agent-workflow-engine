"""LLM provider 注册表入口。

通过 provider 名字懒加载 LangChain ``BaseChatModel``，实现 DSL/CLI 与具体
LLM 厂商解耦。详见 :mod:`agent_engine.llm.providers`。
"""

from agent_engine.llm.providers import ProviderError, get_llm, register_provider

__all__ = ["ProviderError", "get_llm", "register_provider"]
