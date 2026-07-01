"""YAML DSL 加载器与引用完整性校验。

职责：
    1. 读取 YAML 文件并解析为 ``WorkflowDSL`` 对象
    2. 校验引用完整性（entry/finish/depends_on/edges 端点必须存在）
    3. 校验无环（depends_on 不能形成循环依赖）
    4. 错误信息精准定位（哪个节点 / 哪条边 / 哪个字段）

错误信息格式约定：``<定位> <错误类型>: <详细>``，例如：
    - ``节点 'step_a': depends_on 引用了不存在的节点 'step_b'``
    - ``工作流: 检测到循环依赖: step_a -> step_b -> step_a``
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import ValidationError

from agent_engine.dsl.models import (
    EdgeSpec,
    WorkflowDSL,
)

PathLike = str | Path


class DSLError(ValueError):
    """DSL 加载或校验错误的基类。"""


def load_dsl(source: PathLike) -> WorkflowDSL:
    """从 YAML 文件或字符串加载 DSL。

    Args:
        source: YAML 文件路径，或 YAML 文本字符串。

    Returns:
        解析并通过 schema 校验的 ``WorkflowDSL`` 对象。

    Raises:
        DSLError: 文件不存在 / YAML 解析失败 / Pydantic 校验失败。
    """
    text = _read_source(source)
    try:
        raw = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise DSLError(f"YAML 解析失败: {e}") from e
    if not isinstance(raw, dict):
        raise DSLError(f"YAML 顶层必须是字典，实际类型: {type(raw).__name__}")
    try:
        dsl = WorkflowDSL.model_validate(raw)
    except ValidationError as e:
        raise DSLError(_format_pydantic_error(e)) from e
    return dsl


def validate_dsl(dsl: WorkflowDSL) -> None:
    """对已加载的 DSL 做引用完整性与循环依赖校验。

    Args:
        dsl: 已通过 schema 校验的 ``WorkflowDSL``。

    Raises:
        DSLError: 引用了不存在的节点、入口/出口未注册、或存在循环依赖。
    """
    node_ids = {n.id for n in dsl.nodes}
    _check_entry_and_finish(dsl, node_ids)
    _check_depends_on(dsl, node_ids)
    _check_edge_endpoints(dsl, node_ids)
    _check_no_cycles(dsl, node_ids)


# ------------------------------------------------------------------ #
# 内部辅助
# ------------------------------------------------------------------ #


def _read_source(source: PathLike) -> str:
    """统一处理文件路径与文本字符串。"""
    if isinstance(source, Path) or (
        isinstance(source, str) and "\n" not in source and Path(source).is_file()
    ):
        path = Path(source)
        if not path.exists():
            raise DSLError(f"DSL 文件不存在: {path}")
        return path.read_text(encoding="utf-8")
    # 否则视为 YAML 文本
    return str(source)


def _format_pydantic_error(err: ValidationError) -> str:
    """把 Pydantic 校验错误格式化为单行 + 定位。"""
    parts: list[str] = []
    for e in err.errors():
        loc = ".".join(str(p) for p in e["loc"])
        msg = e["msg"]
        parts.append(f"  - 字段 '{loc}': {msg}")
    return "DSL schema 校验失败:\n" + "\n".join(parts)


def _check_entry_and_finish(dsl: WorkflowDSL, node_ids: set[str]) -> None:
    """入口与结束节点必须存在。"""
    if dsl.entry not in node_ids:
        raise DSLError(f"工作流 '{dsl.name}': 入口节点 {dsl.entry!r} 未在 nodes 中定义")
    missing_finish = [f for f in dsl.finish if f not in node_ids]
    if missing_finish:
        raise DSLError(f"工作流 '{dsl.name}': 结束节点 {missing_finish} 未在 nodes 中定义")


def _check_depends_on(dsl: WorkflowDSL, node_ids: set[str]) -> None:
    """每个节点的 depends_on 必须指向已注册节点。"""
    for node in dsl.nodes:
        for dep in node.depends_on:
            if dep == node.id:
                raise DSLError(f"节点 {node.id!r}: depends_on 不能包含自身")
            if dep not in node_ids:
                raise DSLError(f"节点 {node.id!r}: depends_on 引用了不存在的节点 {dep!r}")


def _check_edge_endpoints(dsl: WorkflowDSL, node_ids: set[str]) -> None:
    """显式边的源/目标必须存在（START/END 保留字除外）。"""
    for i, edge in enumerate(dsl.edges):
        _check_edge_endpoint(dsl, edge, "source", edge.source, node_ids, i)
        _check_edge_endpoint(dsl, edge, "target", edge.target, node_ids, i)


def _check_edge_endpoint(
    dsl: WorkflowDSL,
    edge: EdgeSpec,
    endpoint_name: str,
    value: str,
    node_ids: set[str],
    edge_index: int,
) -> None:
    """单端点校验：START/END 允许，否则必须存在。"""
    if value in ("START", "END"):
        return
    if value not in node_ids:
        raise DSLError(
            f"工作流 '{dsl.name}': edges[{edge_index}] 的 "
            f"{endpoint_name}={value!r} 未在 nodes 中定义"
        )


def _check_no_cycles(dsl: WorkflowDSL, node_ids: set[str]) -> None:
    """检测依赖关系是否形成循环（DFS 三色标记法）。

    边的方向约定（执行流方向）：
        - ``edges[i].from -> edges[i].to``：正向边
        - ``node.depends_on = [dep]`` 表示 ``dep -> node``（被依赖者是前置）
    """
    # 邻接表：node -> set of 后继节点
    adj: dict[str, set[str]] = {nid: set() for nid in node_ids}
    # depends_on 反向：被依赖者 → 依赖者
    for n in dsl.nodes:
        for dep in n.depends_on:
            adj[dep].add(n.id)
    # 显式边：source → target
    for edge in dsl.edges:
        if edge.source in adj and edge.target in adj:
            adj[edge.source].add(edge.target)

    WHITE, GRAY, BLACK = 0, 1, 2
    color: dict[str, int] = {nid: WHITE for nid in node_ids}

    def dfs(node: str, path: list[str]) -> None:
        color[node] = GRAY
        path.append(node)
        for nxt in adj.get(node, ()):
            if nxt not in color:
                continue
            if color[nxt] == GRAY:
                # 找到环：从 nxt 到当前 node 截取路径段
                cycle_start = path.index(nxt)
                cycle = path[cycle_start:] + [nxt]
                raise DSLError(f"工作流 '{dsl.name}': 检测到循环依赖: {' -> '.join(cycle)}")
            if color[nxt] == WHITE:
                dfs(nxt, path)
        path.pop()
        color[node] = BLACK

    for nid in node_ids:
        if color[nid] == WHITE:
            dfs(nid, [])


# ------------------------------------------------------------------ #
# 便利函数
# ------------------------------------------------------------------ #


def load_and_validate(source: PathLike) -> WorkflowDSL:
    """一步加载 + 校验的便利函数。"""
    dsl = load_dsl(source)
    validate_dsl(dsl)
    return dsl


__all__ = [
    "DSLError",
    "load_and_validate",
    "load_dsl",
    "validate_dsl",
]
