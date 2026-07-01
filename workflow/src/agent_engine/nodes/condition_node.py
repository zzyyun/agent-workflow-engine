"""Condition 节点：作为 add_conditional_edges 的 path function。

ConditionNode 不直接修改 state，而是评估条件并返回路由目标节点名。
用于 LangGraph 的 ``add_conditional_edges(source, path=condition.evaluate)``。

设计要点：
    - 与现有 ``WorkflowEngine.add_conditional_edges()`` 集成
    - 支持 Python 表达式（lambda / 函数）
    - 提供 fallback 行为（未匹配时返回默认分支）
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agent_engine.nodes.base import NodeAdapter

# 条件函数签名：接收 state，返回布尔值
ConditionFunc = Callable[[dict[str, Any]], bool]


class ConditionNode(NodeAdapter):
    """条件分支评估器。

    使用示例::

        # 简单布尔条件
        cond = ConditionNode(
            condition=lambda s: s.get("value", 0) > 10,
            true_branch="high",
            false_branch="low",
        )
        # 与 WorkflowEngine 集成：
        engine.add_conditional_edges(
            "check",
            path=cond.evaluate,
            path_map={"high": "high_node", "low": "low_node"},
        )
    """

    def __init__(
        self,
        condition: ConditionFunc,
        true_branch: str = "true",
        false_branch: str = "false",
    ) -> None:
        """初始化条件节点。

        Args:
            condition: 接收 state 返回 bool 的函数。
            true_branch: 条件为 True 时返回的路由键（默认 "true"）。
            false_branch: 条件为 False 时返回的路由键（默认 "false"）。
        """
        if not callable(condition):
            raise TypeError(
                f"condition 必须是可调用对象，实际类型: {type(condition).__name__}"
            )
        self.condition = condition
        self.true_branch = true_branch
        self.false_branch = false_branch

    def evaluate(self, state: dict[str, Any]) -> str:
        """评估 state 并返回路由键（用作 path function）。

        Args:
            state: 工作流当前状态。

        Returns:
            ``true_branch`` 或 ``false_branch`` 之一。
        """
        return self.true_branch if self.condition(state) else self.false_branch

    def __call__(self, state: dict[str, Any]) -> dict[str, Any]:
        """作为普通节点调用时不修改 state，仅返回原 state。

        保持与 NodeAdapter 协议一致，但 ConditionNode 主要用途是 ``evaluate()``。
        """
        return state

    def __repr__(self) -> str:
        """可读字符串表示。"""
        return (
            f"ConditionNode(true={self.true_branch!r}, false={self.false_branch!r})"
        )


__all__ = ["ConditionNode", "ConditionFunc"]
