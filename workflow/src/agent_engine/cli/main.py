"""CLI 入口与子命令路由。

使用 Typer 的多命令模式：所有子命令直接挂载在同一个 typer app 上。
"""

from __future__ import annotations

import typer

# 顶层 Typer app
app = typer.Typer(
    name="agent-engine",
    help="Agent Workflow Engine CLI（基于 LangGraph + LangChain）",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main() -> None:
    """Agent Workflow Engine 命令行工具。"""


# 导入子命令（必须在 app 定义之后，确保 @app.command() 装饰器生效）
from agent_engine.cli.commands import resume, run, validate  # noqa: E402, F401

__all__ = ["app", "main"]

if __name__ == "__main__":
    app()
