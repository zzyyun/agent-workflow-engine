"""DSL 数据模型（Pydantic v2）。

设计原则：
    1. 严格类型：所有字段都标注类型，缺失/类型错误由 Pydantic 拦截。
    2. 字段白名单：节点 ``type`` 必须是受支持的短名。
    3. 错误定位：每个节点有 ``id`` 字段，错误信息可回溯到具体节点。
    4. 文档化：每个字段通过 ``Field(description=...)`` 自带文档，
       可由 ``model_json_schema()`` 自动生成 JSON Schema。
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# 节点类型白名单（与 src/agent_engine/nodes/ 下的实现对应）
NodeType = Literal["llm", "tool", "condition", "passthrough"]

# 节点 ID 字段：必填、非空、长度限制
NodeId = Annotated[
    str,
    Field(
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$",
        description="节点唯一标识符（字母数字下划线，非数字开头）",
    ),
]


class RetryPolicy(BaseModel):
    """节点重试策略。"""

    model_config = ConfigDict(extra="forbid")

    max_attempts: int = Field(
        default=3,
        ge=1,
        le=10,
        description="最大重试次数（含首次执行），1 表示不重试",
    )
    backoff_seconds: float = Field(
        default=1.0,
        gt=0.0,
        description="重试间隔基数（指数退避：base * 2^attempt）",
    )


class NodeSpec(BaseModel):
    """DSL 节点定义。"""

    model_config = ConfigDict(extra="forbid")

    id: NodeId = Field(description="节点唯一标识符")
    type: NodeType = Field(description="节点类型短名（llm/tool/condition/passthrough）")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="节点参数（透传给对应节点类型的构造器）",
    )
    depends_on: list[NodeId] = Field(
        default_factory=list,
        description="前置依赖节点 ID 列表（自动建立先后边）",
    )
    retry_policy: RetryPolicy | None = Field(
        default=None,
        description="节点重试策略，未指定时使用引擎默认",
    )
    timeout_seconds: float | None = Field(
        default=None,
        gt=0.0,
        description="节点执行超时（秒），None 表示不限制",
    )


class EdgeSpec(BaseModel):
    """DSL 边定义（用于显式声明非 depends_on 推导的边）。"""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    source: str = Field(
        alias="from",
        description="源节点 ID（或 START 入口常量）",
    )
    target: str = Field(
        alias="to",
        description="目标节点 ID（或 END 出口常量）",
    )
    condition: str | None = Field(
        default=None,
        description="条件边路由键（用于配合 condition 节点的 path_map）",
    )


class WorkflowConfig(BaseModel):
    """工作流引擎配置（与 EngineConfig 对应）。"""

    model_config = ConfigDict(extra="forbid")

    recursion_limit: int = Field(default=25, ge=1, le=1000)
    max_concurrency: int = Field(default=10, ge=1, le=100)


class WorkflowDSL(BaseModel):
    """完整工作流定义。

    YAML 格式示例::

        name: my_workflow
        description: 可选描述
        config:
          recursion_limit: 25
          max_concurrency: 10
        nodes:
          - id: step_a
            type: llm
            params:
              prompt_template: "..."
            depends_on: []
          - id: step_b
            type: tool
            depends_on: [step_a]
            params:
              tool: my_tool
        edges:
          - from: step_a
            to: step_b
        entry: step_a
        finish: [step_b]
    """

    model_config = ConfigDict(extra="forbid")

    name: Annotated[str, Field(min_length=1, max_length=128, description="工作流名称")]
    description: str | None = Field(default=None, max_length=512)
    config: WorkflowConfig = Field(default_factory=WorkflowConfig)
    nodes: list[NodeSpec] = Field(min_length=1, description="节点列表，至少 1 个")
    edges: list[EdgeSpec] = Field(default_factory=list, description="显式边列表")
    entry: NodeId = Field(description="入口节点 ID")
    finish: list[NodeId] = Field(
        default_factory=list,
        description="结束节点 ID 列表（支持多结束点）",
    )

    @field_validator("nodes")
    @classmethod
    def _validate_unique_node_ids(cls, nodes: list[NodeSpec]) -> list[NodeSpec]:
        """节点 ID 必须唯一。"""
        ids = [n.id for n in nodes]
        duplicates = {x for x in ids if ids.count(x) > 1}
        if duplicates:
            raise ValueError(f"节点 ID 重复: {sorted(duplicates)}")
        return nodes


__all__ = [
    "EdgeSpec",
    "NodeSpec",
    "NodeType",
    "RetryPolicy",
    "WorkflowConfig",
    "WorkflowDSL",
]
