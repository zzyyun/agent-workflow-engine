# Examples

本目录提供几个可直接用 `agent-engine` CLI 跑通的端到端 demo，覆盖 Phase 1 支持的全部节点类型。

> 运行前确认已安装：`.venv/Scripts/python.exe -m pip install -e .`（Windows venv via WSL2）。
> CLI 入口：`.venv/Scripts/python.exe -m agent_engine.cli`。

## 1. passthrough 串行工作流 — `cli_demo.yaml`

`step1 (increment) → step2 (double)`，节点用 `module.path:function` 引用 Python 函数。

```bash
.venv/Scripts/python.exe -m agent_engine.cli run examples/cli_demo.yaml \
  --input-file examples/cli_input.json
# 3 -> 4 -> 8
```

## 2. LLM → Tool 串行工作流 — `llm_tool_demo.yaml`

`gen_number (llm, provider=fake) → add_one (tool)`。无需 Python API 预注册：

- `llm` 节点 `params.provider: fake` + `responses: ["10"]`，零依赖（FakeListChatModel）。
- `tool` 节点 `params.tool: examples.demo_nodes:add_one` 引用 `@tool` 装饰对象。
- 切换真实厂商：把 `provider` 改成 `openai`/`anthropic` 并在 params 中传 `model`/`api_key` 等（需安装对应扩展包）。

```bash
.venv/Scripts/python.exe -m agent_engine.cli run examples/llm_tool_demo.yaml \
  --input '{"hint": "any"}'
# number_str="10", result=11
```

## 3. resume 续跑（checkpointer）

`run` 加 `--checkprovider memory/postgres` + `--thread-id` 后会把运行登记到索引，
随后可用 `resume <run_id>` 续跑同一 thread：

```bash
# 进程内（memory，仅供同进程 demo）
.venv/Scripts/python.exe -m agent_engine.cli run examples/cli_demo.yaml \
  --input-file examples/cli_input.json \
  --checkprovider memory --thread-id t1
# 打印 run_id=t1，可 resume
.venv/Scripts/python.exe -m agent_engine.cli resume t1

# 跨进程（postgres，需 PG）
.venv/Scripts/python.exe -m pip install -e '.[postgres]'
.venv/Scripts/python.exe -m agent_engine.cli run examples/cli_demo.yaml \
  --input-file examples/cli_input.json \
  --checkprovider postgres \
  --dsn "postgresql://user:pass@localhost:5432/agent" \
  --thread-id pg-run-1
```

## 节点引用约定速查

| 节点类型 | 关键 params | 引用格式 |
|---|---|---|
| passthrough | `callable` | `module.path:function` |
| llm | `provider` 或 `llm` + `prompt_template` | provider 名 / `module.path:obj` |
| tool | `tool` + `input_key`/`output_key` | `module.path:tool_name` |
| condition | `condition` + `true_branch`/`false_branch` | Python 表达式字符串 |