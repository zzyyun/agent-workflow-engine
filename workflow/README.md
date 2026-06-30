# Agent Workflow Engine

> 一个企业级 AI Agent 工作流引擎（学习导向），基于 LangGraph StateGraph 构建。

## 当前进度

- [x] **Phase 1.1** — LangGraph StateGraph 引擎基础 ([#5](https://github.com/zzyyun/agent-workflow-engine/issues/5))
- [ ] **Phase 1.2** — LangChain 节点适配层 + LLM/Tool/Condition 三节点 ([#6](https://github.com/zzyyun/agent-workflow-engine/issues/6))
- [ ] **Phase 1.3** — YAML DSL + Pydantic Schema 校验 ([#7](https://github.com/zzyyun/agent-workflow-engine/issues/7))
- [ ] **Phase 1.4** — CLI 工具 validate / run / resume ([#8](https://github.com/zzyyun/agent-workflow-engine/issues/8))

## 项目结构

```
workflow/
├── src/                    # 源码
│   └── agent_engine/       # 引擎核心
├── tests/                  # 单元测试
├── examples/               # Demo 与示例
├── docs/                   # PRD 与设计文档
└── README.md
```

## 快速开始

```bash
# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest tests/ -v --cov=src/agent_engine
```

## 技术栈

- **核心框架**: LangGraph (DAG 执行、Checkpoint、Interrupt)
- **节点生态**: LangChain (LLM / Tool / Retriever / Prompt)
- **数据层**: PostgreSQL 16 + PGVector
- **模型**: Mimo v2.5（单一模型，通过 OpenCode API 接入）

## 文档

- [PRD 文档](docs/ai-agent-workflow-engine-prd.md)
