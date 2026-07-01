"""agent-engine resume 子命令：从断点续跑工作流。

工作流程：
    1. 通过 run_id 查运行索引，获取该次运行的 DSL 路径、checkpointer backend、DSN。
    2. 重新加载并构建引擎，挂载相同的 checkpointer（postgres 新建实例读同一持久状态）。
    3. 用相同 thread_id（= run_id）调用 ``invoke(None, ...)`` 续跑。

由于 postgres 跨进程持久化可行；memory saver 仅在单 Python 进程内有效，CLI 跨
进程 resume 仅用于验证命令路径，真正续跑需 postgres。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from agent_engine.checkpointer import CheckpointError, make_checkpointer
from agent_engine.cli.commands._output import print_node_output
from agent_engine.cli.main import app
from agent_engine.cli.run_index import RunNotFoundError, lookup_run
from agent_engine.dsl.builder import BuilderError, build_engine
from agent_engine.dsl.loader import DSLError, load_and_validate


@app.command(name="resume")
def resume_run(
    run_id: str = typer.Argument(..., help="要续跑的运行 ID（即 run 时的 run_id）"),
    dsl_path: Path | None = typer.Option(  # noqa: B008
        None,
        "--dsl",
        help="覆盖索引中的 DSL 路径（默认从运行索引读取）",
    ),
    dsn: str | None = typer.Option(
        None,
        "--dsn",
        help="覆盖索引中的 postgres DSN",
    ),
    output_format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="输出格式：text | json",
    ),
) -> None:
    """从断点续跑工作流。"""
    # 1. 查索引（除非全部手动覆盖仍允许，但 checkprovider 必须从索引或后续推断）
    record: dict[str, Any] | None = None
    try:
        record = lookup_run(run_id)
    except RunNotFoundError as e:
        # 若用户显式提供了 --dsl，则允许脱离索引续跑（仍需 checkprovider 信息）
        if dsl_path is None:
            typer.echo(f"❌ {e}", err=True)
            raise typer.Exit(code=1) from None
        record = {
            "dsl_path": None,
            "checkprovider": None,
            "dsn": None,
            "created_at": 0.0,
        }

    # 2. 确定 DSL 路径与 checkpointer 配置（命令行参数覆盖索引）
    resolved_dsl = dsl_path or (Path(record["dsl_path"]) if record.get("dsl_path") else None)
    if resolved_dsl is None or not Path(resolved_dsl).exists():
        typer.echo(
            f"❌ 找不到 DSL 文件: {resolved_dsl!r}（可通过 --dsl 指定）",
            err=True,
        )
        raise typer.Exit(code=1) from None

    checkprovider = record.get("checkprovider")
    resolved_dsn = dsn if dsn is not None else record.get("dsn")

    # 3. 重建引擎
    try:
        dsl = load_and_validate(Path(resolved_dsl))
    except DSLError as e:
        typer.echo(f"❌ DSL 校验失败: {resolved_dsl}", err=True)
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from None

    try:
        engine = build_engine(dsl)
    except BuilderError as e:
        typer.echo(f"❌ DSL 构建失败: {e}", err=True)
        raise typer.Exit(code=1) from None

    # 4. 挂载同一 checkpointer 后端
    if checkprovider:
        try:
            checkpointer = make_checkpointer(checkprovider, resolved_dsn)
        except CheckpointError as e:
            typer.echo(f"❌ Checkpoint 初始化失败: {e}", err=True)
            raise typer.Exit(code=1) from None
        if checkpointer is None:
            typer.echo(
                f"❌ 运行 {run_id!r} 原本未持久化（checkprovider={checkprovider!r}），无法 resume",
                err=True,
            )
            raise typer.Exit(code=1) from None
        engine = engine.with_checkpointer(checkpointer)
    else:
        typer.echo(
            f"❌ 运行 {run_id!r} 未使用 checkpointer，无可续跑的状态",
            err=True,
        )
        raise typer.Exit(code=1) from None

    # 5. 续跑：传 None state，由 checkpointer 按 thread_id 恢复
    run_config: dict[str, Any] = {"configurable": {"thread_id": run_id}}
    try:
        chunks = list(engine.stream(None, config=run_config))
    except Exception as e:
        typer.echo(f"❌ 续跑失败: {e}", err=True)
        raise typer.Exit(code=1) from None

    # 6. 输出
    final_state = _collect_final_state(chunks, {})
    if output_format == "json":
        typer.echo(
            json.dumps(
                {
                    "ok": True,
                    "run_id": run_id,
                    "workflow": dsl.name,
                    "executed_nodes": len(chunks),
                    "final_state": final_state,
                    "chunks": chunks,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        typer.echo(f"✅ 工作流 {dsl.name!r} 续跑完成 (run_id={run_id})")
        typer.echo("   续跑节点输出:")
        for chunk in chunks:
            print_node_output(chunk)
        typer.echo("   最终 state:")
        typer.echo(json.dumps(final_state, ensure_ascii=False, indent=2))


def _collect_final_state(chunks: list[dict[str, Any]], initial: dict[str, Any]) -> dict[str, Any]:
    """从 stream chunks 合并出最终 state（与 run 命令共用同一逻辑）。"""
    state = dict(initial)
    for chunk in chunks:
        for _node_name, update in chunk.items():
            if isinstance(update, dict):
                state.update(update)
    return state


__all__ = ["resume_run"]
