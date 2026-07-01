"""DSL 加载器与校验器测试。"""

from __future__ import annotations

import pytest

from agent_engine.dsl.loader import (
    DSLError,
    load_and_validate,
    load_dsl,
    validate_dsl,
)
from agent_engine.dsl.models import WorkflowDSL

# ------------------------------------------------------------------ #
# 测试用 YAML fixture
# ------------------------------------------------------------------ #

VALID_YAML = """
name: demo
description: 演示工作流
nodes:
  - id: step_a
    type: passthrough
  - id: step_b
    type: passthrough
    depends_on: [step_a]
  - id: step_c
    type: passthrough
    depends_on: [step_b]
edges:
  - from: step_a
    to: step_b
entry: step_a
finish: [step_c]
"""

VALID_MIN_YAML = """
name: tiny
nodes:
  - id: only
    type: passthrough
entry: only
"""

# 入口节点未定义
MISSING_ENTRY = """
name: bad
nodes:
  - id: a
    type: passthrough
entry: nonexistent
"""

# depends_on 引用不存在的节点
BAD_DEPENDS = """
name: bad
nodes:
  - id: a
    type: passthrough
    depends_on: [ghost]
entry: a
"""

# 节点类型白名单
UNKNOWN_TYPE = """
name: bad
nodes:
  - id: a
    type: not_a_real_type
entry: a
"""

# 循环依赖：A -> B -> A
CYCLE = """
name: bad
nodes:
  - id: a
    type: passthrough
    depends_on: [b]
  - id: b
    type: passthrough
    depends_on: [a]
entry: a
"""

# 边的端点不存在
BAD_EDGE = """
name: bad
nodes:
  - id: a
    type: passthrough
edges:
  - from: a
    to: ghost
entry: a
"""

# depends_on 自引用
SELF_DEP = """
name: bad
nodes:
  - id: a
    type: passthrough
    depends_on: [a]
entry: a
"""


@pytest.fixture
def tmp_yaml(tmp_path, request):
    """把 YAML 文本写到临时文件并返回路径。"""
    p = tmp_path / "workflow.yaml"
    p.write_text(request.param, encoding="utf-8")
    return p


# ------------------------------------------------------------------ #
# load_dsl 测试
# ------------------------------------------------------------------ #


class TestLoadDSL:
    """load_dsl 行为测试。"""

    def test_load_from_string(self) -> None:
        """从 YAML 字符串加载。"""
        dsl = load_dsl(VALID_MIN_YAML)
        assert isinstance(dsl, WorkflowDSL)
        assert dsl.name == "tiny"
        assert len(dsl.nodes) == 1

    def test_load_from_file(self, tmp_path) -> None:
        """从 YAML 文件加载。"""
        p = tmp_path / "wf.yaml"
        p.write_text(VALID_YAML, encoding="utf-8")
        dsl = load_dsl(p)
        assert dsl.name == "demo"
        assert len(dsl.nodes) == 3

    def test_load_missing_file_raises(self, tmp_path) -> None:
        """文件不存在应抛 DSLError。"""
        with pytest.raises(DSLError, match="不存在"):
            load_dsl(tmp_path / "nope.yaml")

    def test_load_invalid_yaml_raises(self) -> None:
        """YAML 语法错误应抛 DSLError。"""
        with pytest.raises(DSLError, match="YAML 解析失败"):
            load_dsl("nodes: [unclosed")

    def test_load_top_level_not_dict_raises(self) -> None:
        """YAML 顶层不是字典应抛错。"""
        with pytest.raises(DSLError, match="顶层必须是字典"):
            load_dsl("- just\n- a\n- list\n")

    def test_load_schema_error_mentions_field(self) -> None:
        """schema 校验失败应指出具体字段。"""
        with pytest.raises(DSLError) as exc_info:
            load_dsl(UNKNOWN_TYPE)
        msg = str(exc_info.value)
        # 应包含 type 字段
        assert "type" in msg
        # 应包含 schema 校验失败的提示
        assert "校验失败" in msg or "validation" in msg.lower()


# ------------------------------------------------------------------ #
# validate_dsl 测试
# ------------------------------------------------------------------ #


class TestValidateDSL:
    """validate_dsl 引用完整性测试。"""

    def test_valid_dsl_passes(self) -> None:
        """合法 DSL 校验通过。"""
        dsl = load_dsl(VALID_YAML)
        validate_dsl(dsl)  # 不抛错即通过

    def test_missing_entry_raises(self) -> None:
        """入口节点未定义应抛错（明确错误信息）。"""
        dsl = load_dsl(MISSING_ENTRY)
        with pytest.raises(DSLError) as exc_info:
            validate_dsl(dsl)
        assert "入口节点" in str(exc_info.value)
        assert "nonexistent" in str(exc_info.value)

    def test_missing_finish_raises(self) -> None:
        """结束节点未定义应抛错。"""
        yaml_text = """
        name: bad
        nodes:
          - id: a
            type: passthrough
        entry: a
        finish: [ghost]
        """
        dsl = load_dsl(yaml_text)
        with pytest.raises(DSLError, match="结束节点"):
            validate_dsl(dsl)

    def test_bad_depends_on_raises(self) -> None:
        """depends_on 引用不存在的节点应抛错（明确错误信息）。"""
        dsl = load_dsl(BAD_DEPENDS)
        with pytest.raises(DSLError) as exc_info:
            validate_dsl(dsl)
        msg = str(exc_info.value)
        assert "节点" in msg
        assert "ghost" in msg

    def test_self_depends_on_raises(self) -> None:
        """depends_on 自引用应抛错。"""
        dsl = load_dsl(SELF_DEP)
        with pytest.raises(DSLError, match="不能包含自身"):
            validate_dsl(dsl)

    def test_bad_edge_endpoint_raises(self) -> None:
        """边的端点未定义应抛错。"""
        dsl = load_dsl(BAD_EDGE)
        with pytest.raises(DSLError) as exc_info:
            validate_dsl(dsl)
        msg = str(exc_info.value)
        assert "edges" in msg
        assert "ghost" in msg

    def test_edge_with_start_and_end_allowed(self) -> None:
        """边的端点可为 START/END 保留字。"""
        yaml_text = """
        name: ok
        nodes:
          - id: a
            type: passthrough
          - id: b
            type: passthrough
        edges:
          - from: START
            to: a
          - from: a
            to: b
          - from: b
            to: END
        entry: a
        finish: [b]
        """
        dsl = load_dsl(yaml_text)
        validate_dsl(dsl)  # 不抛错

    def test_cycle_detection_raises(self) -> None:
        """循环依赖应被检测并报错（明确指出环路）。"""
        dsl = load_dsl(CYCLE)
        with pytest.raises(DSLError) as exc_info:
            validate_dsl(dsl)
        msg = str(exc_info.value)
        assert "循环依赖" in msg
        # 错误信息应包含环上节点
        assert "a" in msg and "b" in msg

    def test_self_loop_raises(self) -> None:
        """单节点自循环（A -> A）应被检测。"""
        yaml_text = """
        name: bad
        nodes:
          - id: a
            type: passthrough
        edges:
          - from: a
            to: a
        entry: a
        """
        dsl = load_dsl(yaml_text)
        with pytest.raises(DSLError, match="循环依赖"):
            validate_dsl(dsl)


# ------------------------------------------------------------------ #
# load_and_validate 集成测试
# ------------------------------------------------------------------ #


class TestLoadAndValidate:
    """一步加载 + 校验的便利函数。"""

    def test_valid_yaml_loads_and_validates(self, tmp_path) -> None:
        """合法 YAML：一步通过。"""
        p = tmp_path / "wf.yaml"
        p.write_text(VALID_YAML, encoding="utf-8")
        dsl = load_and_validate(p)
        assert dsl.name == "demo"

    def test_invalid_yaml_raises(self, tmp_path) -> None:
        """非法 YAML：一步抛错。"""
        p = tmp_path / "bad.yaml"
        p.write_text(CYCLE, encoding="utf-8")
        with pytest.raises(DSLError, match="循环依赖"):
            load_and_validate(p)
