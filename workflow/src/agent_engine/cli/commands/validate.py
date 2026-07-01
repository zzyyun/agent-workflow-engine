"""agent-engine validate 子命令：校验 DSL 文件。"""

from __future__ import annotations

import json
from pathlib import Path

import typer

from agent_engine.cli.main import app
from agent_engine.dsl.loader import DSLError, load_and_validate


@app.command(name="validate")
def validate_dsl(
    dsl_path: Path = typer.Argument(  # noqa: B008
        ...,
        help="DSL 文件路径（YAML）",
        exists=True,
        readable=True,
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="以 JSON 格式输出校验结果（CI 友好）",
    ),
) -> None:
    """校验 DSL 文件的 schema 与引用完整性。"""
    try:
        dsl = load_and_validate(dsl_path)
    except DSLError as e:
        if json_output:
            typer.echo(
                json.dumps(
                    {"ok": False, "file": str(dsl_path), "errors": [str(e)]},
                    ensure_ascii=False,
                    indent=2,
                )
            )
        else:
            typer.echo(f"❌ DSL 校验失败: {dsl_path}", err=True)
            typer.echo(str(e), err=True)
        raise typer.Exit(code=1) from None

    # 成功：输出结果
    if json_output:
        typer.echo(
            json.dumps(
                {
                    "ok": True,
                    "file": str(dsl_path),
                    "name": dsl.name,
                    "nodes": len(dsl.nodes),
                    "edges": len(dsl.edges),
                    "entry": dsl.entry,
                    "finish": dsl.finish,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        typer.echo(f"✅ DSL 校验通过: {dsl_path}")
        typer.echo(f"   工作流: {dsl.name}")
        typer.echo(f"   节点数: {len(dsl.nodes)}")
        typer.echo(f"   边数:   {len(dsl.edges)}")
        typer.echo(f"   入口:   {dsl.entry}")
        typer.echo(f"   出口:   {dsl.finish or '(无)'}")


__all__ = ["validate_dsl"]
