"""引擎配置与异常类型定义。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngineConfig:
    """WorkflowEngine 运行时配置。

    Attributes:
        recursion_limit: 引擎最大递归步数，防止节点进入死循环。默认 25。
        max_concurrency: 并行节点的最大并发度。默认 10。
        raise_on_cycle: 当检测到无法收敛的循环时是否抛出异常。默认 True。
    """

    # 递归步数上限，LangGraph 调用图的最大深度
    recursion_limit: int = 25
    # 并发上限：同时执行的节点任务数
    max_concurrency: int = 10
    # 遇到死循环时是否直接抛错
    raise_on_cycle: bool = True

    def __post_init__(self) -> None:
        """校验配置参数合法性。"""
        if self.recursion_limit <= 0:
            raise ValueError(
                f"recursion_limit 必须为正整数, 实际值: {self.recursion_limit}"
            )
        if self.max_concurrency <= 0:
            raise ValueError(
                f"max_concurrency 必须为正整数, 实际值: {self.max_concurrency}"
            )


class EngineError(Exception):
    """引擎相关错误的基类。"""


class NodeAlreadyExistsError(EngineError):
    """重复注册同名节点时抛出。"""


class NodeNotFoundError(EngineError):
    """引用了未注册的节点时抛出。"""


class EdgeError(EngineError):
    """边定义错误时抛出。"""


__all__ = [
    "EdgeError",
    "EngineConfig",
    "EngineError",
    "NodeAlreadyExistsError",
    "NodeNotFoundError",
]
