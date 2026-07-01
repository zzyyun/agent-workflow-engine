"""ConditionNode 单元测试。"""

from __future__ import annotations

import pytest

from agent_engine.nodes.condition_node import ConditionNode


class TestConditionNode:
    """ConditionNode 行为测试。"""

    def test_evaluate_true_branch(self) -> None:
        """条件为 True 时返回 true_branch。"""
        cond = ConditionNode(
            condition=lambda s: s.get("value", 0) > 10,
            true_branch="high",
            false_branch="low",
        )
        assert cond.evaluate({"value": 20}) == "high"

    def test_evaluate_false_branch(self) -> None:
        """条件为 False 时返回 false_branch。"""
        cond = ConditionNode(
            condition=lambda s: s.get("value", 0) > 10,
            true_branch="high",
            false_branch="low",
        )
        assert cond.evaluate({"value": 5}) == "low"

    def test_default_branch_names(self) -> None:
        """默认分支名为 'true' / 'false'。"""
        cond = ConditionNode(condition=lambda s: s["x"] == 1)
        assert cond.evaluate({"x": 1}) == "true"
        assert cond.evaluate({"x": 0}) == "false"

    def test_call_does_not_modify_state(self) -> None:
        """__call__ 不修改 state（保持原样返回）。"""
        cond = ConditionNode(condition=lambda s: True)
        state = {"key": "value", "num": 42}
        result = cond(state)
        assert result == state
        assert result is state  # 同一对象引用

    def test_works_with_complex_condition(self) -> None:
        """复杂条件：多键组合判断。"""
        cond = ConditionNode(
            condition=lambda s: s.get("score", 0) >= 60 and s.get("attempts", 0) < 3,
            true_branch="pass",
            false_branch="retry",
        )
        assert cond.evaluate({"score": 80, "attempts": 1}) == "pass"
        assert cond.evaluate({"score": 80, "attempts": 5}) == "retry"
        assert cond.evaluate({"score": 40, "attempts": 1}) == "retry"

    def test_non_callable_condition_raises(self) -> None:
        """condition 不可调用时抛 TypeError。"""
        with pytest.raises(TypeError, match="可调用对象"):
            ConditionNode(condition="not callable")  # type: ignore[arg-type]

    def test_evaluate_is_path_function_compatible(self) -> None:
        """evaluate() 签名与 LangGraph path function 兼容：单参数返回字符串。"""
        cond = ConditionNode(
            condition=lambda s: "key" in s,
            true_branch="has_key",
            false_branch="no_key",
        )
        # LangGraph path function 接收 state 返回字符串
        result = cond.evaluate({"key": 1})
        assert isinstance(result, str)
        assert result == "has_key"

    def test_repr_includes_branches(self) -> None:
        """__repr__ 输出分支名便于调试。"""
        cond = ConditionNode(
            condition=lambda s: True,
            true_branch="yes",
            false_branch="no",
        )
        r = repr(cond)
        assert "ConditionNode" in r
        assert "'yes'" in r
        assert "'no'" in r
