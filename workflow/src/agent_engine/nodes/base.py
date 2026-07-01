"""节点适配器基类。

所有自定义节点都应继承 ``NodeAdapter`` 并实现 ``__call__`` 方法。
节点协议与 LangGraph 兼容：接收 state 字典，返回更新后的 state 字典。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.runnables import Runnable, RunnableLambda


class NodeAdapter(ABC):
    """节点抽象基类。

    设计目标：
        1. 统一 ``invoke(state) -> state`` 接口，与 LangGraph 节点协议对齐。
        2. 屏蔽 LangChain Runnable 细节，让节点作者聚焦业务逻辑。
        3. 可被 ``WorkflowEngine.add_node()`` 直接使用，也可转为 Runnable 嵌入 LangGraph。
    """

    @abstractmethod
    def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """执行节点逻辑，返回更新后的 state。

        Args:
            state: 工作流当前状态字典。

        Returns:
            更新后的 state 字典。
        """
        raise NotImplementedError

    def to_runnable(self) -> Runnable:
        """将节点转为 LangChain ``Runnable``，可嵌入 LangGraph。"""
        return RunnableLambda(self.__call__)


__all__ = ["NodeAdapter"]
