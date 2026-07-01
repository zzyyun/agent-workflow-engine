"""运行索引：记录每次带 checkpointer 的 CLI 运行，供 ``resume`` 查找。

存储位置：``~/.agent_engine/runs.json``，结构::

    {
      "run-<uuid>": {
        "dsl_path": "/abs/path/workflow.yaml",
        "checkprovider": "memory" | "postgres" | null,
        "dsn": "postgresql://..." | null,
        "created_at": 1234567890.0
      }
    }

写入采用 ``.tmp`` + 原子 ``os.replace``，并对不可序列化字段做守卫。
索引文件缺失/损坏时自动重置为空（不影响 CLI 主流程）。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# 索引文件目录与文件名
_DIR = Path.home() / ".agent_engine"
_INDEX_FILE = _DIR / "runs.json"


class RunNotFoundError(KeyError):
    """resume 指定的 run_id 在索引中不存在。"""


def load_index() -> dict[str, dict[str, Any]]:
    """读取运行索引；文件缺失或损坏时返回空 dict。"""
    if not _INDEX_FILE.exists():
        return {}
    try:
        text = _INDEX_FILE.read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, json.JSONDecodeError):
        # 已存在的索引损坏：宁可丢弃也不阻塞用户运行
        return {}
    if not isinstance(data, dict):
        return {}
    # 兼容历史结构：保证 value 是 dict
    out: dict[str, dict[str, Any]] = {}
    for k, v in data.items():
        if isinstance(v, dict):
            out[str(k)] = v
    return out


def save_index(index: dict[str, dict[str, Any]]) -> None:
    """原子写入运行索引。

    通过 ``.tmp`` 文件 + ``os.replace`` 保证写不撕裂；目录不存在时创建。
    """
    _DIR.mkdir(parents=True, exist_ok=True)
    tmp = _INDEX_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, _INDEX_FILE)


def record_run(
    run_id: str,
    dsl_path: str,
    checkprovider: str | None,
    dsn: str | None,
    created_at: float,
) -> None:
    """登记一次运行到索引（覆盖同 id）。"""
    index = load_index()
    index[run_id] = {
        "dsl_path": dsl_path,
        "checkprovider": checkprovider,
        "dsn": dsn,
        "created_at": created_at,
    }
    save_index(index)


def lookup_run(run_id: str) -> dict[str, Any]:
    """查询单个 run_id 的记录。

    Raises:
        RunNotFoundError: run_id 不在索引中。
    """
    index = load_index()
    if run_id not in index:
        raise RunNotFoundError(
            f"未找到运行 {run_id!r}，请确认 run_id 正确，或先通过 "
            f"'agent-engine run --checkprovider ...' 启动一次持久化运行。"
        )
    return index[run_id]


__all__ = ["RunNotFoundError", "load_index", "lookup_run", "record_run", "save_index"]
