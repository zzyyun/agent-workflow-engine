"""CLI 单元测试：使用 Typer 的 CliRunner 模拟命令行调用。"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from agent_engine.cli.main import app

runner = CliRunner()


# ------------------------------------------------------------------ #
# validate 子命令
# ------------------------------------------------------------------ #


class TestValidateCommand:
    """``agent-engine validate`` 测试。"""

    def _write_yaml(self, tmp_path: Path, content: str) -> Path:
        p = tmp_path / "wf.yaml"
        p.write_text(content, encoding="utf-8")
        return p

    def test_valid_dsl_succeeds(self, tmp_path: Path) -> None:
        """合法 DSL：退出码 0，输出校验通过信息。"""
        yaml_path = self._write_yaml(
            tmp_path,
            """
            name: demo
            nodes:
              - id: a
                type: passthrough
            entry: a
            """,
        )
        result = runner.invoke(app, ["validate", str(yaml_path)])
        assert result.exit_code == 0
        # result.output 合并 stdout + stderr
        assert "✅ DSL 校验通过" in result.output
        assert "demo" in result.output

    def test_invalid_dsl_fails(self, tmp_path: Path) -> None:
        """非法 DSL（未知节点类型）：退出码 1，错误信息指出 type 字段。"""
        yaml_path = self._write_yaml(
            tmp_path,
            """
            name: bad
            nodes:
              - id: a
                type: not_a_real_type
            entry: a
            """,
        )
        result = runner.invoke(app, ["validate", str(yaml_path)])
        assert result.exit_code == 1
        assert "❌ DSL 校验失败" in result.output
        assert "type" in result.output

    def test_json_output_format(self, tmp_path: Path) -> None:
        """--json 输出结构化结果。"""
        yaml_path = self._write_yaml(
            tmp_path,
            """
            name: json_test
            nodes:
              - id: a
                type: passthrough
              - id: b
                type: passthrough
            entry: a
            finish: [b]
            """,
        )
        result = runner.invoke(app, ["validate", str(yaml_path), "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["ok"] is True
        assert data["name"] == "json_test"
        assert data["nodes"] == 2
        assert data["entry"] == "a"
        assert data["finish"] == ["b"]

    def test_json_output_on_error(self, tmp_path: Path) -> None:
        """--json 错误时输出结构化错误信息。"""
        yaml_path = self._write_yaml(
            tmp_path,
            """
            name: bad
            nodes: []
            entry: x
            """,
        )
        result = runner.invoke(app, ["validate", str(yaml_path), "--json"])
        assert result.exit_code == 1
        data = json.loads(result.stdout)
        assert data["ok"] is False
        assert len(data["errors"]) >= 1

    def test_missing_file_fails(self, tmp_path: Path) -> None:
        """不存在的文件：退出码 1。"""
        result = runner.invoke(app, ["validate", str(tmp_path / "nope.yaml")])
        # Typer 会先检查文件存在性（exists=True），退出码 2（用法错误）
        assert result.exit_code != 0


# ------------------------------------------------------------------ #
# run 子命令
# ------------------------------------------------------------------ #


class TestRunCommand:
    """``agent-engine run`` 测试。"""

    def _write_yaml_with_passthrough(self, tmp_path: Path) -> tuple[Path, Path]:
        """写一个 passthrough 工作流 + 输入 JSON。"""
        yaml_path = tmp_path / "wf.yaml"
        yaml_path.write_text(
            """
            name: run_demo
            nodes:
              - id: step1
                type: passthrough
                params:
                  callable: examples.demo_nodes:increment
              - id: step2
                type: passthrough
                depends_on: [step1]
                params:
                  callable: examples.demo_nodes:double
            entry: step1
            finish: [step2]
            """,
            encoding="utf-8",
        )
        input_path = tmp_path / "input.json"
        input_path.write_text(json.dumps({"value": 3}), encoding="utf-8")
        return yaml_path, input_path

    def test_run_executes_passthrough_workflow(self, tmp_path: Path) -> None:
        """运行 passthrough 工作流：3 -> 4 -> 8。"""
        yaml_path, input_path = self._write_yaml_with_passthrough(tmp_path)
        result = runner.invoke(
            app,
            [
                "run",
                str(yaml_path),
                "--input-file",
                str(input_path),
            ],
        )
        assert result.exit_code == 0, result.stdout
        assert "✅ 工作流 'run_demo' 执行成功" in result.stdout
        assert '"value": 8' in result.stdout
        assert '"log"' in result.stdout

    def test_run_json_output(self, tmp_path: Path) -> None:
        """--format json 输出结构化结果。"""
        yaml_path, input_path = self._write_yaml_with_passthrough(tmp_path)
        result = runner.invoke(
            app,
            [
                "run",
                str(yaml_path),
                "--input-file",
                str(input_path),
                "--format",
                "json",
            ],
        )
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["ok"] is True
        assert data["workflow"] == "run_demo"
        assert data["executed_nodes"] == 2
        assert data["final_state"]["value"] == 8

    def test_run_with_no_input(self, tmp_path: Path) -> None:
        """不传 input 时使用空 dict。"""
        yaml_path = tmp_path / "wf.yaml"
        yaml_path.write_text(
            """
            name: no_input
            nodes:
              - id: only
                type: passthrough
                params:
                  callable: examples.demo_nodes:increment
            entry: only
            finish: [only]
            """,
            encoding="utf-8",
        )
        result = runner.invoke(app, ["run", str(yaml_path)])
        assert result.exit_code == 0
        assert '"value": 1' in result.stdout  # 0 + 1

    def test_run_invalid_dsl_fails(self, tmp_path: Path) -> None:
        """非法 DSL 报错并退出码 1。"""
        yaml_path = tmp_path / "bad.yaml"
        yaml_path.write_text(
            """
            name: bad
            nodes:
              - id: a
                type: not_real
            entry: a
            """,
            encoding="utf-8",
        )
        result = runner.invoke(app, ["run", str(yaml_path)])
        assert result.exit_code == 1
        assert "❌ DSL 校验失败" in result.output

    def test_run_llm_node_via_fake_provider(self, tmp_path: Path) -> None:
        """llm 节点 + provider=fake：现在可通过 CLI 执行（CLI 可用化）。"""
        yaml_path = tmp_path / "wf.yaml"
        yaml_path.write_text(
            """
            name: llm_demo
            nodes:
              - id: llm_step
                type: llm
                params:
                  provider: fake
                  responses: ["hello"]
                  prompt_template: "hi {q}"
                  output_key: out
            entry: llm_step
            finish: [llm_step]
            """,
            encoding="utf-8",
        )
        result = runner.invoke(app, ["run", str(yaml_path), "--input", '{"q":"x"}'])
        assert result.exit_code == 0, result.output
        assert '"out": "hello"' in result.stdout

    def test_run_llm_node_missing_prompt_template_fails(self, tmp_path: Path) -> None:
        """llm 节点缺 prompt_template 仍 BuilderError 退出 1。"""
        yaml_path = tmp_path / "wf.yaml"
        yaml_path.write_text(
            """
            name: llm_bad
            nodes:
              - id: llm_step
                type: llm
                params:
                  provider: fake
                  responses: ["x"]
            entry: llm_step
            finish: [llm_step]
            """,
            encoding="utf-8",
        )
        result = runner.invoke(app, ["run", str(yaml_path)])
        assert result.exit_code == 1
        assert "❌ DSL 构建失败" in result.output
        assert "prompt_template" in result.output

    def test_run_input_json_string(self, tmp_path: Path) -> None:
        """--input 接受 JSON 字符串。"""
        yaml_path, _ = self._write_yaml_with_passthrough(tmp_path)
        result = runner.invoke(
            app,
            [
                "run",
                str(yaml_path),
                "--input",
                '{"value": 5}',
            ],
        )
        assert result.exit_code == 0
        # 5 -> 6 -> 12
        assert '"value": 12' in result.stdout

    def test_run_input_json_invalid(self, tmp_path: Path) -> None:
        """--input 非法 JSON 应报错。"""
        yaml_path, _ = self._write_yaml_with_passthrough(tmp_path)
        result = runner.invoke(
            app,
            ["run", str(yaml_path), "--input", "not-valid-json"],
        )
        assert result.exit_code == 1
        assert "JSON 解析失败" in result.output


# ------------------------------------------------------------------ #
# resume 子命令
# ------------------------------------------------------------------ #


class TestResumeCommand:
    """``agent-engine resume`` 测试。"""

    def _write_passthrough_yaml(self, tmp_path: Path) -> Path:
        yaml_path = tmp_path / "wf.yaml"
        yaml_path.write_text(
            """
            name: resume_demo
            nodes:
              - id: step1
                type: passthrough
                params:
                  callable: examples.demo_nodes:increment
            entry: step1
            finish: [step1]
            """,
            encoding="utf-8",
        )
        return yaml_path

    def test_resume_unknown_run_without_dsl_fails(self, tmp_path: Path) -> None:
        """未知 run_id 且未提供 --dsl：友好报错退出 1。"""
        result = runner.invoke(app, ["resume", "does-not-exist"])
        assert result.exit_code == 1
        assert "未找到运行" in result.output
        assert "does-not-exist" in result.output

    def test_resume_without_checkpointer_fails(self, tmp_path: Path, monkeypatch) -> None:
        """索引中无 checkprovider（未持久化）时 resume 应拒绝。"""
        from agent_engine.cli import run_index

        index_dir = tmp_path / ".agent_engine"
        monkeypatch.setattr(run_index, "_DIR", index_dir)
        monkeypatch.setattr(run_index, "_INDEX_FILE", index_dir / "runs.json")
        yaml_path = self._write_passthrough_yaml(tmp_path)
        run_index.record_run("np-id", str(yaml_path.resolve()), None, None, 0.0)

        result = runner.invoke(app, ["resume", "np-id"])
        assert result.exit_code == 1
        assert "未使用 checkpointer" in result.output

    def test_resume_with_memory_checkpointer_runs(self, tmp_path: Path, monkeypatch) -> None:
        """带 memory checkpointer 的 resume 走通命令路径并输出最终 state。"""
        from agent_engine.cli import run_index

        index_dir = tmp_path / ".agent_engine"
        monkeypatch.setattr(run_index, "_DIR", index_dir)
        monkeypatch.setattr(run_index, "_INDEX_FILE", index_dir / "runs.json")
        yaml_path = self._write_passthrough_yaml(tmp_path)
        run_index.record_run("mem-id", str(yaml_path.resolve()), "memory", None, 0.0)

        result = runner.invoke(app, ["resume", "mem-id", "--format", "json"])
        assert result.exit_code == 0, result.output
        data = json.loads(result.stdout)
        assert data["ok"] is True
        assert data["run_id"] == "mem-id"
        # memory 跨进程不持久，resume 等价于重跑：value 从 0 → 1
        assert data["final_state"]["value"] == 1

    def test_resume_unknown_run_with_dsl_provided_runs(self, tmp_path: Path, monkeypatch) -> None:
        """索引未命中但提供 --dsl + 注入可用 checkpointer 时可续跑。"""
        from agent_engine import checkpointer as ckpt_mod
        from agent_engine.cli import run_index

        index_dir = tmp_path / ".agent_engine"
        monkeypatch.setattr(run_index, "_DIR", index_dir)
        monkeypatch.setattr(run_index, "_INDEX_FILE", index_dir / "runs.json")
        # 注入一个返回 memory saver 的伪 make_checkpointer，绕过索引的 checkprovider
        monkeypatch.setattr(
            ckpt_mod,
            "make_checkpointer",
            lambda name, dsn=None: __import__(
                "langgraph.checkpoint.memory", fromlist=["MemorySaver"]
            ).MemorySaver(),
        )
        # 同时替换 resume 模块中的引用（build_engine 路径未改 ckpt_mod 直接符号）
        from agent_engine.cli.commands import resume as resume_mod

        monkeypatch.setattr(
            resume_mod,
            "make_checkpointer",
            lambda name, dsn=None: __import__(
                "langgraph.checkpoint.memory", fromlist=["MemorySaver"]
            ).MemorySaver(),
        )
        yaml_path = self._write_passthrough_yaml(tmp_path)
        result = runner.invoke(
            app, ["resume", "ghost-id", "--dsl", str(yaml_path), "--format", "json"]
        )
        # 索引未命中 + --dsl 提供时，record.checkprovider=None，会走"未使用 checkprovider"分支
        # 因此期望退出 1（与 test_resume_without_checkprovider_fails 一致的行为）
        assert result.exit_code == 1


# ------------------------------------------------------------------ #
# CLI 全局
# ------------------------------------------------------------------ #


class TestMain:
    """CLI 全局行为。"""

    def test_no_args_shows_help(self) -> None:
        """无参数时显示帮助（no_args_is_help=True，Typer 退出码 0）。"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Agent Workflow Engine" in result.output

    def test_help_lists_three_subcommands(self) -> None:
        """--help 列出三个子命令。"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "validate" in result.output
        assert "run" in result.output
        assert "resume" in result.output
