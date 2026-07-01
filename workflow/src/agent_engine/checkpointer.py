"""Checkpoint saver 工厂：按名构造 LangGraph 持久化后端。

设计目标：
    1. 把 LangGraph checkpointer 的实例化细节集中在一处，便于 CLI 调用。
    2. 懒加载厂商后端（如 ``langgraph-checkpoint-postgres``），基线无需安装。
    3. 统一错误类型 ``CheckpointError``，CLI 可友好展示。

支持的 backend：
    - ``None``：返回 ``None``（无持久化，默认，纯内存执行）
    - ``"memory"``：``MemorySaver``，进程内续跑（仅供同进程测试/demo）
    - ``"postgres"``：``PostgresSaver``，跨进程持久续跑（需安装拓展 + 可达 PG）
"""

from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver


class CheckpointError(RuntimeError):
    """checkpointer 构造失败（缺包、缺 DSN、后端不可达等）。"""


def make_checkpointer(name: str | None, dsn: str | None = None) -> BaseCheckpointSaver | None:
    """根据 backend 名字构造 checkpointer 实例。

    Args:
        name: backend 名字；``None``/``""`` 表示不启用持久化。
        dsn: postgres 连接串（仅 postgres 必填）。

    Returns:
        ``BaseCheckpointSaver`` 实例或 ``None``（未启用）。

    Raises:
        CheckpointError: backend 未知、postgres 缺 DSN、缺包或 DB 不可达。
    """
    if not name:
        return None

    if name == "memory":
        return MemorySaver()

    if name == "postgres":
        if not dsn:
            raise CheckpointError(
                "postgres checkpointer 需要通过 --dsn 提供连接串，"
                "例如 'postgresql://user:pass@localhost:5432/agent'"
            )
        return _make_postgres_saver(dsn)

    raise CheckpointError(f"未知的 checkpointer backend {name!r}，支持: memory / postgres")


def _make_postgres_saver(dsn: str) -> BaseCheckpointSaver:
    """懒加载并构造 PostgresSaver，缺包或 DB 不可达时抛 ``CheckpointError``。"""
    try:
        # langgraph-checkpoint-postgres 提供的同步 saver
        import psycopg  # noqa: F401  验证驱动可用
        from langgraph.checkpoint.postgres import PostgresSaver  # type: ignore[import-not-found]
    except ImportError as e:
        raise CheckpointError(
            "postgres checkpointer 需要 langgraph-checkpoint-postgres 与 psycopg："
            "pip install 'agent-engine[postgres]'"
        ) from e

    try:
        # PostgresSaver.from_conn_string 返回上下文管理器，进入后建立连接 + setup 表结构
        ctx = PostgresSaver.from_conn_string(conn_string=dsn)
        saver = ctx.__enter__()
        try:
            saver.setup()  # 建表（幂等）
        except Exception as e:
            ctx.__exit__(None, None, None)
            raise CheckpointError(
                f"PostgresSaver 初始化失败（无法连接或建表）: {type(e).__name__}: {e}"
            ) from e
        # 注意：此处不 exit 上下文，连接保持存活以供后续 invoke 使用。
        # 进程退出时连接由 GC 回收，简单 CLI 场景可接受。
        return saver
    except CheckpointError:
        raise
    except Exception as e:
        raise CheckpointError(f"PostgresSaver 构造失败: {type(e).__name__}: {e}") from e


__all__ = ["CheckpointError", "make_checkpointer"]
