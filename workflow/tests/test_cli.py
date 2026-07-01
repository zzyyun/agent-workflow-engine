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

    def test_run_unsupported_node_type_raises_builder_error(
        self, tmp_path: Path
    ) -> None:
        """LLM 节点在 CLI 中应抛 BuilderError（Phase 2 实现）。"""
        yaml_path = tmp_path / "wf.yaml"
        yaml_path.write_text(
            """
            name: llm_demo
            nodes:
              - id: llm_step
                type: llm
                params:
                  prompt_template: "hi"
                  output_key: out
            entry: llm_step
            finish: [llm_step]
            """,
            encoding="utf-8",
        )
        result = runner.invoke(app, ["run", str(yaml_path)])
        assert result.exit_code == 1
        assert "LLM 节点需通过 Python API 预注册" in result.output

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
    """``agent-engine resume`` 测试（Phase 1 占位）。"""

    def test_resume_returns_stub_message(self) -> None:
        """resume 子命令返回占位信息并退出码 1。"""
        result = runner.invoke(app, ["resume", "run-12345"])
        assert result.exit_code == 1
        assert "暂未实现" in result.output
        assert "run-12345" in result.output
        assert "PostgresSaver" in result.output  # 提示 Phase 2 计划


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
