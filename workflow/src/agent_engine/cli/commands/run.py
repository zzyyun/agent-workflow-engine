"""agent-engine run 子命令：执行 DSL 工作流。"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import typer

from agent_engine.checkpointer import CheckpointError, make_checkpointer
from agent_engine.cli.commands._output import print_node_output
from agent_engine.cli.main import app
from agent_engine.cli.run_index import record_run
from agent_engine.dsl.builder import BuilderError, build_engine
from agent_engine.dsl.loader import DSLError, load_and_validate


@app.command(name="run")
def run_dsl(
    dsl_path: Path = typer.Argument(  # noqa: B008
        ...,
        help="DSL 文件路径（YAML）",
        exists=True,
        readable=True,
    ),
    input_json: str | None = typer.Option(
        None,
        "--input",
        "-i",
        help='初始 state 的 JSON 字符串（如 \'{"key": "value"}\'）',
    ),
    input_file: Path | None = typer.Option(  # noqa: B008
        None,
        "--input-file",
        help="从 JSON 文件读取初始 state",
    ),
    output_format: str = typer.Option(
        "text",
        "--format",
        "-f",
        help="输出格式：text（人类可读）| json（结构化）",
    ),
    checkprovider: str | None = typer.Option(  # noqa: B008
        None,
        "--checkprovider",
        help="checkpoint 后端：memory（进程内）| postgres（跨进程，需 --dsn）；"
        "省略则不持久化、不可 resume",
    ),
    dsn: str | None = typer.Option(
        None,
        "--dsn",
        help="postgres 连接串（仅 --checkprovider postgres 时必填）",
    ),
    thread_id: str | None = typer.Option(
        None,
        "--thread-id",
        help="续跑 thread 标识；省略时自动生成 run-<uuid>，并登记到运行索引",
    ),
) -> None:
    """执行 DSL 工作流并输出结果。"""
    # 1. 解析 input
    try:
        initial_state = _parse_input(input_json, input_file)
    except ValueError as e:
        typer.echo(f"❌ 输入参数错误: {e}", err=True)
        raise typer.Exit(code=1) from None

    # 2. 加载 + 校验 DSL
    try:
        dsl = load_and_validate(dsl_path)
    except DSLError as e:
        typer.echo(f"❌ DSL 校验失败: {dsl_path}", err=True)
        typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from None

    # 3. 构建 WorkflowEngine
    try:
        engine = build_engine(dsl)
    except BuilderError as e:
        typer.echo(f"❌ DSL 构建失败: {e}", err=True)
        raise typer.Exit(code=1) from None

    # 4. 挂载 checkpointer（可选）
    try:
        checkpointer = make_checkpointer(checkprovider, dsn)
    except CheckpointError as e:
        typer.echo(f"❌ Checkpoint 初始化失败: {e}", err=True)
        raise typer.Exit(code=1) from None
    if checkpointer is not None:
        engine = engine.with_checkpointer(checkpointer)

    # 5. 确定 thread_id（resume 续跑的标识）
    run_id = thread_id or f"run-{uuid.uuid4()}"
    run_config: dict[str, Any] = {"configurable": {"thread_id": run_id}}

    # 6. 执行
    try:
        # 使用 stream 模式获取每个节点的输出（用于详细展示）
        chunks = list(engine.stream(initial_state, config=run_config))
    except Exception as e:
        typer.echo(f"❌ 工作流执行失败: {e}", err=True)
        raise typer.Exit(code=1) from None

    # 7. 登记 run 索引（仅当启用了 checkpointer 才可 resume）
    if checkpointer is not None:
        record_run(
            run_id=run_id,
            dsl_path=str(dsl_path.resolve()),
            checkprovider=checkprovider,
            dsn=dsn,
            created_at=0.0,  # CLI 不依赖时间戳；占用字段便于未来扩展
        )

    # 8. 输出结果
    final_state = _collect_final_state(chunks, initial_state)
    if output_format == "json":
        typer.echo(
            json.dumps(
                {
                    "ok": True,
                    "workflow": dsl.name,
                    "run_id": run_id if checkpointer is not None else None,
                    "executed_nodes": len(chunks),
                    "final_state": final_state,
                    "chunks": chunks,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        typer.echo(f"✅ 工作流 {dsl.name!r} 执行成功")
        if checkpointer is not None:
            typer.echo(f"   run_id: {run_id}（可用 `agent-engine resume {run_id}` 续跑）")
        typer.echo("   节点输出:")
        for chunk in chunks:
            print_node_output(chunk)
        typer.echo("   最终 state:")
        typer.echo(json.dumps(final_state, ensure_ascii=False, indent=2))


def _parse_input(input_json: str | None, input_file: Path | None) -> dict[str, Any]:
    """解析 --input 与 --input-file 参数，返回初始 state。"""
    if input_json and input_file:
        raise ValueError("--input 与 --input-file 互斥")
    if not input_json and not input_file:
        return {}
    if input_file:
        if not input_file.exists():
            raise ValueError(f"输入文件不存在: {input_file}")
        text = input_file.read_text(encoding="utf-8")
    else:
        text = input_json
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 解析失败: {e}") from e
    if not isinstance(data, dict):
        raise ValueError(f"输入必须是 JSON object, 实际类型: {type(data).__name__}")
    return data


def _collect_final_state(chunks: list[dict[str, Any]], initial: dict[str, Any]) -> dict[str, Any]:
    """从 stream chunks 合并出最终 state。

    每个 chunk 形如 ``{"node_name": {"key": "value", ...}}``，表示该节点
    对 state 的更新。把所有 chunk 合并到 initial 上即得最终 state。
    """
    state = dict(initial)
    for chunk in chunks:
        for _node_name, update in chunk.items():
            if isinstance(update, dict):
                state.update(update)
    return state


__all__ = ["run_dsl"]
