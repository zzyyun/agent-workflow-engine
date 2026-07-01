"""输出格式化工具。"""

from __future__ import annotations

import json
from typing import Any

import typer


def print_node_output(chunk: dict[str, Any]) -> None:
    """格式化输出单个 stream chunk。"""
    for node_name, update in chunk.items():
        typer.echo(f"     - {node_name}: {json.dumps(update, ensure_ascii=False)}")


__all__ = ["print_node_output"]
