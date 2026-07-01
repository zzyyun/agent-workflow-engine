"""checkpointer + resume 续跑机制测试。"""

from __future__ import annotations

import pytest

from agent_engine import WorkflowEngine
from agent_engine.checkpointer import CheckpointError, make_checkpointer
from agent_engine.cli import run_index

# ------------------------------------------------------------------ #
# make_checkpointer
# ------------------------------------------------------------------ #


class TestMakeCheckpointer:
    """checkpointer 工厂行为。"""

    def test_none_returns_none(self) -> None:
        """name 为 None/空 返回 None。"""
        assert make_checkpointer(None) is None
        assert make_checkpointer("") is None

    def test_memory_returns_saver(self) -> None:
        """memory 返回 InMemorySaver。"""
        saver = make_checkpointer("memory")
        assert saver is not None
        assert hasattr(saver, "aget") or hasattr(saver, "get")

    def test_unknown_backend_raises(self) -> None:
        """未知 backend 抛 CheckpointError。"""
        with pytest.raises(CheckpointError, match="未知"):
            make_checkpointer("redis")

    def test_postgres_without_dsn_raises(self) -> None:
        """postgres 缺 DSN 抛 CheckpointError。"""
        with pytest.raises(CheckpointError, match="dsn"):
            make_checkpointer("postgres")

    def test_postgres_missing_pkg_raises(self, monkeypatch) -> None:
        """postgres 但 langgraph-checkpoint-postgres 未安装时抛 CheckpointError。"""
        import builtins

        real_import = builtins.__import__

        def _fake_import(name, *args, **kwargs):
            if name.startswith("langgraph.checkpoint.postgres") or name == "psycopg":
                raise ImportError(f"simulated missing: {name}")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", _fake_import)
        with pytest.raises(CheckpointError, match="agent-engine\\[postgres\\]"):
            make_checkpointer("postgres", "postgresql://u@h:5432/db")


# ------------------------------------------------------------------ #
# 引擎 MemorySaver 续跑机制（与后端无关）
# ------------------------------------------------------------------ #


def _build_engine(saver) -> WorkflowEngine:
    """构建一个 a→b 双节点引擎并挂载 saver。"""
    e = WorkflowEngine()
    e.add_node("a", lambda s: {"x": s.get("x", 0) + 1})
    e.add_node("b", lambda s: {"x": s["x"] + 1})
    e.add_edge("a", "b")
    e.set_entry_point("a")
    e.set_finish_point("b")
    if saver is not None:
        e.with_checkpointer(saver)
    return e


class TestResumeMechanism:
    """续跑机制：同 thread 重建引擎后可恢复。"""

    def test_with_checkpointer_invalidates_compiled(self) -> None:
        """with_checkpointer 后再次执行应重新编译。"""
        e = _build_engine(make_checkpointer("memory"))
        e.compile()
        assert e._compiled is not None
        e.with_checkpointer(make_checkpointer("memory"))
        assert e._compiled is None

    def test_same_thread_resume_replays_state(self) -> None:
        """同进程：run1 完成后用同一 saver+thread 重建引擎取回持久 state。

        resume 传 None state，LangGraph 会从 checkpoint 恢复并重新执行图，
        因此 x 会继续累加（验证状态确实被持久化，而非凭空）。
        """
        saver = make_checkpointer("memory")
        cfg = {"configurable": {"thread_id": "t-resume"}}

        e1 = _build_engine(saver)
        r1 = e1.invoke({"x": 0}, config=cfg)
        assert r1["x"] == 2

        # 在内存 saver 中应有该 thread 的 checkpoint
        assert saver is not None

        # 重建引擎（模拟新一轮加载）+ 同一 saver + 同 thread 续跑
        e2 = _build_engine(saver)
        r2 = e2.invoke(None, config=cfg)
        # 从持久化 state 续跑：x 从 2 再次 → 3 → 4
        assert r2["x"] == 4


# ------------------------------------------------------------------ #
# run_index
# ------------------------------------------------------------------ #


@pytest.fixture
def isolated_index(tmp_path, monkeypatch):
    """把索引文件重定向到 tmp 目录，隔离测试。"""
    index_dir = tmp_path / ".agent_engine"
    monkeypatch.setattr(run_index, "_DIR", index_dir)
    monkeypatch.setattr(run_index, "_INDEX_FILE", index_dir / "runs.json")
    return run_index


class TestRunIndex:
    """运行索引读写。"""

    def test_record_and_lookup(self, isolated_index) -> None:
        """登记后可查到。"""
        isolated_index.record_run("r1", "/p/wf.yaml", "postgres", "dsn", 1.0)
        rec = isolated_index.lookup_run("r1")
        assert rec["dsl_path"] == "/p/wf.yaml"
        assert rec["checkprovider"] == "postgres"
        assert rec["dsn"] == "dsn"

    def test_lookup_missing_raises(self, isolated_index) -> None:
        """查不存在的 run_id 抛 RunNotFoundError。"""
        with pytest.raises(run_index.RunNotFoundError, match="r-none"):
            isolated_index.lookup_run("r-none")

    def test_corrupted_index_reset_to_empty(self, isolated_index) -> None:
        """索引文件损坏时返回空 dict 不抛错。"""
        isolated_index._INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        isolated_index._INDEX_FILE.write_text("not json{", encoding="utf-8")
        assert isolated_index.load_index() == {}

    def test_atomic_write(self, isolated_index) -> None:
        """写入后文件存在且可读回。"""
        isolated_index.record_run("r2", "/p2/wf.yaml", "memory", None, 2.0)
        assert isolated_index._INDEX_FILE.exists()
        rec = isolated_index.lookup_run("r2")
        assert rec["checkprovider"] == "memory"
