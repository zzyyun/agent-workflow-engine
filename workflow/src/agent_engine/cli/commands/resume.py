"""agent-engine resume 子命令（Phase 1 占位）。"""

from __future__ import annotations

import typer

from agent_engine.cli.main import app


@app.command(name="resume")
def resume_run(
    run_id: str = typer.Argument(..., help="要续跑的运行 ID"),
) -> None:
    """从断点续跑工作流。Phase 1 仅占位（NotImplemented）。"""
    typer.echo(
        f"⚠️  resume {run_id!r} 暂未实现\n"
        f"   Phase 1 计划：本任务为占位\n"
        f"   Phase 2 计划：集成 LangGraph PostgresSaver，"
        f"提供 PostgreSQL Checkpoint 持久化 + 续跑能力\n"
        f"   详见 docs/ai-agent-workflow-engine-prd.md Story 2"
    )
    raise typer.Exit(code=1)


__all__ = ["resume_run"]
