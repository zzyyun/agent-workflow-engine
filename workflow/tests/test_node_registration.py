"""WorkflowEngine 节点注册相关测试。"""

from __future__ import annotations

import pytest

from agent_engine import (
    NodeAlreadyExistsError,
    WorkflowEngine,
)


class TestNodeRegistration:
    """节点注册相关 API 测试。"""

    def test_add_single_node(self) -> None:
        """可注册单个节点。"""
        engine = WorkflowEngine()
        result = engine.add_node("a", lambda s: s)
        # 支持链式调用
        assert result is engine
        assert engine.has_node("a")
        assert engine.node_names == ["a"]

    def test_add_multiple_nodes(self) -> None:
        """可注册多个节点。"""
        engine = WorkflowEngine()
        engine.add_node("a", lambda s: s)
        engine.add_node("b", lambda s: s)
        engine.add_node("c", lambda s: s)
        assert engine.node_names == ["a", "b", "c"]

    def test_duplicate_node_raises(self) -> None:
        """重复注册同名节点应抛 NodeAlreadyExistsError。"""
        engine = WorkflowEngine()
        engine.add_node("a", lambda s: s)
        with pytest.raises(NodeAlreadyExistsError, match="节点 'a' 已存在"):
            engine.add_node("a", lambda s: s)

    def test_invalid_node_name_raises(self) -> None:
        """非法节点名应抛 ValueError。"""
        engine = WorkflowEngine()
        with pytest.raises(ValueError, match="非空字符串"):
            engine.add_node("", lambda s: s)

    def test_invalid_action_raises(self) -> None:
        """action 不是可调用对象时应抛 ValueError。"""
        engine = WorkflowEngine()
        with pytest.raises(ValueError, match="可调用对象"):
            engine.add_node("a", "not callable")  # type: ignore[arg-type]

    def test_reserved_node_name_raises(self) -> None:
        """LangGraph 保留字（START/END）不可作为节点名。"""
        from langgraph.graph import END, START

        engine = WorkflowEngine()
        with pytest.raises(ValueError, match="保留字"):
            engine.add_node(START, lambda s: s)  # type: ignore[arg-type]
        with pytest.raises(ValueError, match="保留字"):
            engine.add_node(END, lambda s: s)  # type: ignore[arg-type]
