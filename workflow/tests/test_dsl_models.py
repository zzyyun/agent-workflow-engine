"""DSL 模型层单元测试。"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from agent_engine.dsl.models import (
    EdgeSpec,
    NodeSpec,
    RetryPolicy,
    WorkflowConfig,
    WorkflowDSL,
)


class TestNodeSpec:
    """NodeSpec 字段校验。"""

    def test_minimal_node(self) -> None:
        """最小节点：仅 id + type。"""
        node = NodeSpec(id="step_a", type="llm")
        assert node.id == "step_a"
        assert node.type == "llm"
        assert node.params == {}
        assert node.depends_on == []
        assert node.retry_policy is None
        assert node.timeout_seconds is None

    def test_all_supported_types(self) -> None:
        """type 字段必须是受支持的短名。"""
        for t in ("llm", "tool", "condition", "passthrough"):
            node = NodeSpec(id="x", type=t)  # type: ignore[arg-type]
            assert node.type == t

    def test_unsupported_type_rejected(self) -> None:
        """未知类型应被 Pydantic 拒绝。"""
        with pytest.raises(ValidationError) as exc_info:
            NodeSpec(id="x", type="unknown_type")  # type: ignore[arg-type]
        assert "type" in str(exc_info.value).lower()

    def test_empty_id_rejected(self) -> None:
        """空 ID 应被拒绝。"""
        with pytest.raises(ValidationError):
            NodeSpec(id="", type="llm")

    def test_invalid_id_pattern_rejected(self) -> None:
        """含特殊字符的 ID 应被拒绝。"""
        with pytest.raises(ValidationError):
            NodeSpec(id="step-a", type="llm")  # 含连字符
        with pytest.raises(ValidationError):
            NodeSpec(id="1step", type="llm")  # 数字开头
        with pytest.raises(ValidationError):
            NodeSpec(id="step a", type="llm")  # 含空格

    def test_extra_fields_rejected(self) -> None:
        """未声明字段应被禁止（避免拼写错误）。"""
        with pytest.raises(ValidationError):
            NodeSpec(id="x", type="llm", unknown_field=42)  # type: ignore[call-arg]

    def test_retry_policy_optional(self) -> None:
        """retry_policy 可选；提供时校验字段。"""
        node = NodeSpec(
            id="x",
            type="tool",
            retry_policy=RetryPolicy(max_attempts=5, backoff_seconds=2.0),
        )
        assert node.retry_policy is not None
        assert node.retry_policy.max_attempts == 5

    def test_invalid_retry_attempts_rejected(self) -> None:
        """max_attempts 必须 >= 1。"""
        with pytest.raises(ValidationError):
            RetryPolicy(max_attempts=0)

    def test_timeout_must_be_positive(self) -> None:
        """timeout_seconds 必须 > 0（None 表示无限制）。"""
        with pytest.raises(ValidationError):
            NodeSpec(id="x", type="llm", timeout_seconds=0)
        with pytest.raises(ValidationError):
            NodeSpec(id="x", type="llm", timeout_seconds=-1.0)


class TestEdgeSpec:
    """EdgeSpec 字段校验。"""

    def test_simple_edge(self) -> None:
        """普通边：from + to。"""
        edge = EdgeSpec(**{"from": "a", "to": "b"})
        assert edge.source == "a"
        assert edge.target == "b"
        assert edge.condition is None

    def test_conditional_edge(self) -> None:
        """条件边：可指定 condition 字段。"""
        edge = EdgeSpec(**{"from": "a", "to": "b", "condition": "high"})
        assert edge.condition == "high"


class TestWorkflowDSL:
    """WorkflowDSL 顶层校验。"""

    def test_minimal_workflow(self) -> None:
        """最小工作流：name + nodes + entry。"""
        dsl = WorkflowDSL(
            name="test",
            nodes=[NodeSpec(id="a", type="passthrough")],
            entry="a",
        )
        assert dsl.name == "test"
        assert len(dsl.nodes) == 1
        assert dsl.edges == []
        assert dsl.finish == []
        assert isinstance(dsl.config, WorkflowConfig)

    def test_duplicate_node_ids_rejected(self) -> None:
        """节点 ID 重复应被拒绝。"""
        with pytest.raises(ValidationError) as exc_info:
            WorkflowDSL(
                name="test",
                nodes=[
                    NodeSpec(id="a", type="passthrough"),
                    NodeSpec(id="a", type="tool"),
                ],
                entry="a",
            )
        assert "重复" in str(exc_info.value)

    def test_at_least_one_node_required(self) -> None:
        """至少 1 个节点。"""
        with pytest.raises(ValidationError):
            WorkflowDSL(name="test", nodes=[], entry="a")

    def test_extra_fields_rejected(self) -> None:
        """未声明的顶层字段应被拒绝。"""
        with pytest.raises(ValidationError):
            WorkflowDSL(
                name="test",
                nodes=[NodeSpec(id="a", type="passthrough")],
                entry="a",
                unknown_field="oops",  # type: ignore[call-arg]
            )

    def test_json_schema_generation(self) -> None:
        """可生成 JSON Schema（PRD 验收标准之一）。"""
        schema = WorkflowDSL.model_json_schema()
        assert "properties" in schema
        assert "nodes" in schema["properties"]
        assert "entry" in schema["properties"]
