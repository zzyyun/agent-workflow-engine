# Product Requirements Document: AI Agent 工作流引擎

**Version**: 1.7
**Date**: 2026-06-29
**Author**: Sarah (Product Owner)
**Quality Score**: 96/100
**Status**: 待评审
**变更说明**: v1.7 - 移除阿里云云端部署（轻量应用服务器 + 宝塔 + CI/CD + 域名），聚焦"从 GitHub 拉取 → 本地一键部署运行"的完整体验

---

## Executive Summary

本项目旨在构建一个**企业级 AI Agent 工作流引擎**（学习导向），从根本上解决传统单轮 LLM 对话模式无法胜任的多步骤、有依赖、带分支、需断点续跑的复杂业务场景。

引擎通过 **YAML/JSON DSL** 与**可视化低代码画布**双形态，为开发者与业务运营人员提供一致的使用体验。系统以 DAG 为执行模型，原生支持意图识别、LLM 调用、工具调用、RAG 检索、条件分支、循环迭代、人工审批等十余种节点类型，并配套**状态持久化（PostgreSQL）+ 断点续跑 + Webhook 通知 + 可视化执行轨迹**等企业级能力。

**学习项目定位**：通过 **OpenCode 接入 Mimo v2.5**（单一模型，统一 API Key 调用），中文能力强，长上下文友好，订阅制固定成本。核心框架采用 **LangGraph + LangChain**（DAG 执行、Checkpoint、Vector Store 等企业级能力开箱即用，大幅降低自研成本），数据层使用 **PostgreSQL 16 + PGVector**（关系数据 + 向量检索统一），硬件门槛低（单台开发机即可跑通），追求代码简洁可读 > 性能极致。典型应用场景包括：自动报表生成、工单处理、数据巡检、文档批量处理等需要长时运行、多步依赖、需人工把关的企业流水线。

**部署形态**：**仅本地部署**，通过 Docker Compose 一键启动（API + PostgreSQL+pgvector）。完整流程是 `git clone` → `cp .env.example .env` → `make setup` → `docker compose up` → 访问 `http://localhost:8000`，整个过程 < 5 分钟。**不涉及任何云端服务**，所有数据（工作流定义、执行历史、向量索引）全部存储在用户本机。

---

## Problem Statement

### Current Situation（当前痛点）

- **传统单轮 Agent 的局限**：单次 Prompt + 单次响应的模式无法处理需要"先检索、再规划、再调用、再校验"的多步骤流程。
- **缺乏状态管理**：LLM 调用失败、网络抖动、Token 限额耗尽等场景下，整个任务被迫从头开始，企业场景下成本与体验均不可接受。
- **无人工把关机制**：金融、合规、对外发送等关键动作无法要求人工审批确认，AI 不可控风险高。
- **可视化能力薄弱**：业务方看不懂代码、研发方不愿写死流程，二者缺乏共同语言。
- **重复造轮子**：每条业务线都要自己写一套调度、状态、重试、告警，资源浪费严重。

### Proposed Solution（解决方案）

构建一套**通用 AI Agent 工作流引擎**，提供：

- **统一的 DAG 执行内核**：基于 **LangGraph** 的 StateGraph，节点驱动、有向有环图、并行调度、串行编排、原生 Checkpoint 与 Human-in-the-Loop。
- **丰富的节点生态**：基于 **LangChain** 的 Tool / Retriever / Prompt 模板生态，原生支持 LLM、工具调用、RAG 检索、条件分支、循环迭代、人工审批等十余种节点类型。
- **完整的工程化能力**：DSL 校验、Schema 管理、断点续跑、重试与补偿、告警通知、审计日志。
- **双形态接入**：开发者用 DSL，运营用画布，二者共享同一份执行语义。
- **单机 Docker Compose 部署**：5 分钟内启动整套服务（API + PostgreSQL+PGVector + Web），零依赖上手。

### Business Impact（业务价值）

- **效率提升**：把原本需要多周开发的 AI 任务流水线缩短到天级配置。
- **成本降低**：避免每条业务线重复建设调度与重试基础设施，研发投入减少 60%+。
- **风险可控**：人工审批 + 审计日志让 AI 能力可放心进入金融/合规等高敏场景。
- **可观测**：执行轨迹全留痕，事后追溯与优化有据可依。

---

## Success Metrics

### Primary KPIs（三维度）

#### 1. 业务效果维度
- **场景覆盖数**：MVP 上线 90 天内，支撑 ≥ 5 个真实业务场景（自动报表、工单、数据巡检、文档处理、巡检告警）。
- **人工替代率**：在覆盖场景中，AI 自动完成的工作量占总工作量 ≥ 70%。
- **任务成功率**：业务任务从启动到完成一次通过的成功率 ≥ 85%。

#### 2. 产品覆盖维度
- **节点丰富度**：MVP 阶段覆盖 ≥ 8 类核心节点（LLM / Tool / Condition / Loop / Retriever / Approval / HTTP / SubWorkflow）。
- **DSL 完备性**：能用 DSL 描述任意复杂业务流（嵌套循环 + 分支 + 审批），无能力盲点。
- **画布可用性**：业务人员通过画布搭出可用工作流，不需写代码。
- **场景化模板**：提供 ≥ 3 个开箱即用模板（每日巡检、批量文档处理、自动报表）。

#### 3. 技术指标维度
- **单节点执行延迟**：P95 ≤ 2 秒（不含外部 API 调用）。
- **并行任务端到端延迟**：P95 ≤ 5 分钟（10 步以内流程）。
- **并发能力**：支持 ≥ 20 个工作流实例并发执行（PostgreSQL 16 配独立连接池）。
- **可靠性**：进程崩溃后能 100% 续跑，重试 + 补偿后任务最终一致。
- **可观测覆盖率**：100% 任务实例可查询、可重放、可追溯。
- **冷启动时间**：引擎从启动到可接受 API 请求 < 3 秒（PostgreSQL 容器常驻）。
- **资源占用**：空闲时内存 < 200MB（LLM 走 OpenCode 云端，无需本地资源）。

#### 4. 学习项目专项指标
- **本地可跑通率**：100%（仅需 Docker + OpenCode API Key 即可完整跑通）。
- **学习曲线**：30 分钟内能让新开发者从零搭出第一个工作流。
- **代码可读性**：核心模块单文件 < 500 行，命名清晰，注释率 ≥ 30%。
- **成本可控**：OpenCode 订阅制固定月费，**无 token 成本焦虑**，无单次调用费用上限。
- **模型切换成本**：**单一 Mimo v2.5 模型策略**，不引入多模型路由，简化心智。Phase 1 完成后如发现能力短板再考虑扩展。

#### 5. 本地部署专项指标
- **首次启动时间**：从 `git clone` 到服务可用 < **5 分钟**（含 Docker 镜像拉取 + 依赖安装 + 容器启动）。
- **零云依赖**：所有组件（API + DB + 向量）均本地运行，无需联网即可使用除 LLM 外的所有功能。
- **环境变量最少化**：用户只需配置 `OPENCODE_API_KEY` 即可启动全部功能（其他均有默认值）。
- **跨平台支持**：macOS / Linux / WSL2 / Windows 11 (WSL2) 均可运行。
- **数据本地化**：所有数据（工作流、Checkpoint、向量索引）存储在 `./data/` 目录，用户可备份/迁移。
- **升级路径**：`git pull` + `make setup` + `docker compose pull && up -d` 即可平滑升级。
- **回滚能力**：保留最近 3 个 Docker 镜像版本，支持 `docker compose down` 后切回旧版本。
- **硬件要求**：最低 4GB 内存 + 10GB 磁盘（学习与轻量业务场景）。

#### 6. 框架与数据层专项指标
- **LangGraph 适配度**：核心 DAG 能力（状态机、循环、分支、Checkpoint、Interrupt）100% 来自 LangGraph，自研代码 ≤ 30%。
- **LangChain 复用度**：LLM / Tool / Retriever / Prompt 模板 90%+ 走 LangChain，避免重复造轮子。
- **PGVector 性能**：单表 10 万向量下，TopK=5 检索 P95 ≤ 200ms。
- **Embedding 一致性**：写入与检索使用同一模型（langchain 集成 `OpenAIEmbeddings` + PGVector）。
- **混合检索支持**：向量相似度 + PostgreSQL 全文检索（tsvector）可联合查询。

### Validation（验证方法）

- MVP 验收：通过模拟场景（≥ 3 个）端到端跑通，记录耗时、成功率。
- 用户验收：邀请 ≥ 2 个业务方在画布上搭出真实流程并跑通。
- 性能压测：用 Locust/Wrk 跑并发 10 任务的压测脚本，记录 P95 与成功率。

---

## User Personas

### Primary: 平台开发者（Developer）

- **角色**：负责搭建 AI 工作流的后端/平台工程师。
- **目标**：通过 DSL 快速定义复杂业务流，集成到现有业务系统中。
- **痛点**：每次写新业务都要重新搭调度、写状态机、加重试，重复劳动。
- **技术能力**：中高级，熟悉 Python、YAML、Git、Docker。
- **使用形态**：YAML/JSON DSL、CLI、SDK、API。

### Secondary: 业务运营/分析师（Business Operator）

- **角色**：业务线的产品经理、数据分析师、运营人员。
- **目标**：不写代码，用画布快速搭出"取数 → AI 总结 → 发 Webhook"之类的流程。
- **痛点**：现有方案要么纯写代码门槛高，要么纯界面功能弱，难以两全。
- **技术能力**：低代码友好型，会用 Excel 与 Notion，不写 Python。
- **使用形态**：可视化画布（拖拽节点、连线、配置参数）。

### Tertiary: 业务系统集成方（Integrator）

- **角色**：上游业务系统（如 CRM、工单系统）通过 API 触发工作流。
- **目标**：把工作流引擎嵌入既有产品，触发任务、查询状态、接收回调。
- **痛点**：需要清晰、稳定的 API + Webhook 契约。
- **技术能力**：高级，熟悉 REST/HTTP、Webhook、SDK。
- **使用形态**：OpenAPI 文档、SDK、Webhook 回调。

---

## User Stories & Acceptance Criteria

### Story 1: DSL 编写与执行

**As a** 平台开发者
**I want to** 在 YAML 中定义一个完整的工作流（含 LLM、Tool、Condition 三种节点）
**So that** 我能复用同一份定义在不同环境跑、纳入版本管理

**Acceptance Criteria:**
- [ ] DSL 支持定义节点（id、type、params、depends_on、retry_policy、timeout）。
- [ ] 启动前自动校验 Schema、依赖关系，发现错误立即报错。
- [ ] 提供 CLI：`agent run workflow.yaml --input '{...}'` 一键执行。
- [ ] 执行完成后输出结构化结果（包含每节点输入/输出/耗时）。
- [ ] DSL 通过 JSON Schema 校验，文档化所有节点类型与参数。

### Story 2: 断点续跑

**As a** 平台开发者
**I want to** 进程崩溃后能从未完成的节点继续执行
**So that** 不浪费已消耗的 LLM 调用与时间

**Acceptance Criteria:**
- [ ] 使用 **LangGraph `PostgresSaver`** 作为 Checkpoint 存储，状态持久化到 PostgreSQL。
- [ ] 引擎重启后，可通过 `agent resume <run_id>` 从断点续跑（LangGraph `thread_id` 机制）。
- [ ] 已成功的节点自动跳过（幂等），失败的节点按策略重试或等待人工。
- [ ] 断点续跑后，最终结果与首次完整执行等价。

### Story 3: 人工审批节点

**As a** 业务运营
**I want to** 在关键节点（如对外发送）暂停任务，等我审批后再继续
**So that** AI 不会在无人监管下做出高风险动作

**Acceptance Criteria:**
- [ ] Approval 节点触发后，任务状态置为 `WAITING_APPROVAL`。
- [ ] 通知通过 Webhook 发出（钉钉/Slack/飞书等），含审批链接。
- [ ] 审批人点击链接可查看上下文、Approve / Reject / 修改参数后再继续。
- [ ] 审批超时（可配置默认 24h）自动按策略处理（默认拒绝 + 告警）。
- [ ] 审批结果作为节点输出进入下游。

### Story 4: 条件分支与循环

**As a** 平台开发者
**I want to** 在工作流中表达"如果 X 则走 A 分支，否则走 B 分支"和"对列表中的每项执行子流程"
**So that** 能描述真实业务中的复杂逻辑

**Acceptance Criteria:**
- [ ] Condition 节点支持 Python 表达式或 JSONPath 条件判断。
- [ ] Loop 节点支持遍历数组（For-Each）与条件循环（While）。
- [ ] Loop 内部可嵌套子工作流（SubWorkflow 节点）。
- [ ] 循环单次执行有独立重试策略，单次失败不影响整体。
- [ ] 循环聚合（Aggregate）结果按规则合并到下游。

### Story 5: RAG 检索节点

**As a** 业务运营
**I want to** 在工作流中检索企业知识库，喂给 LLM 生成更准的答案
**So that** 业务问答不再"凭空胡说"

**Acceptance Criteria:**
- [ ] Retriever 节点基于 **LangChain `PGVector`**，向量与元数据统一存于 PostgreSQL。
- [ ] 支持文档上传 → 自动分块 → Embedding → 入库（langchain `OpenAIEmbeddings` 或本地模型）。
- [ ] 支持按 Query 检索 TopK，结果作为节点输出。
- [ ] 支持可选的 ReRank / Score Threshold。
- [ ] 检索过程可在执行轨迹中可视化（Query、召回数、TopK 结果）。

### Story 6: 可视化画布

**As a** 业务运营
**I want to** 拖拽节点、连线，搭出工作流并保存
**So that** 不写代码也能用上引擎

**Acceptance Criteria:**
- [ ] 左侧节点面板：拖拽 8 类核心节点到画布。
- [ ] 右侧参数面板：选中节点后可视化编辑参数（输入框、下拉、JSON 编辑器）。
- [ ] 画布与 DSL 双向同步：画布编辑→DSL、DSL 导入→画布。
- [ ] 保存后立即可用 API 触发执行，画布上能看执行状态。
- [ ] 节点连线规则：自动校验（如 Loop 内部不能直接引用外部变量）。

### Story 7: 执行历史与可视化轨迹

**As a** 平台开发者 / 业务运营
**I want to** 在 Web 界面查看任意历史任务的执行轨迹
**So that** 失败时能快速定位问题、成功时能复用最佳实践

**Acceptance Criteria:**
- [ ] 任务列表页：按时间、状态、Workflow 名筛选。
- [ ] 任务详情页：拓扑视图（DAG 节点带状态色：绿/黄/红/灰）+ 时间轴。
- [ ] 节点详情：输入、输出、耗时、Token 用量、日志链接。
- [ ] 支持"重跑该任务"与"从该节点重跑"两个动作。
- [ ] 历史数据保留至少 30 天（可配置）。

### Story 8: 告警与通知

**As a** 业务运营
**I want to** 在任务失败、审批超时、重试超限时收到通知
**So that** 第一时间介入处理

**Acceptance Criteria:**
- [ ] 告警通道：Webhook（可对接钉钉/Slack/飞书）+ 控制台输出。
- [ ] 告警粒度：Workflow 级 / 节点级 / Run 级。
- [ ] 告警模板可配置（标题、内容、@人员）。
- [ ] 支持告警静默（如非工作时间降级为仅控制台输出）。
- [ ] 告警历史可查，便于复盘。

---

## Functional Requirements

### Core Features

#### Feature 1: 工作流执行引擎（DAG Runtime）

- **Description**：基于 **LangGraph `StateGraph`** 的工作流执行内核，节点驱动、依赖解析、并行调度、状态管理、Checkpoint 与 Human-in-the-Loop 开箱即用。
- **User flow**：
  1. 加载 DSL（YAML/JSON）→ 解析为内部 StateGraph。
  2. 校验 Schema、依赖、参数，发现错误立即返回。
  3. 通过 `add_node` / `add_edge` / `add_conditional_edges` 构建图。
  4. 编译为可执行 `CompiledGraph`，绑定 `PostgresSaver` 作为 Checkpointer。
  5. 通过 `graph.invoke()` / `graph.stream()` 驱动执行。
  6. 全局结束 → 汇总结果 → 触发下游通知。
- **Edge cases**：
  - 节点超时：LangGraph 内置 `timeout` 配置 + 重试策略。
  - 死循环：LangGraph `recursion_limit` 默认 25，可配置。
  - 资源不足：LangGraph `max_concurrency` 控制并行度。
- **Error handling**：
  - 节点失败走 LangGraph `RetryPolicy`（指数退避）。
  - 关键节点失败 → LangGraph `interrupt_before` 暂停 + 人工介入。
  - 状态恢复：`graph.get_state(thread_id)` 续跑。
- **核心价值**：自研代码量减少 60%+，LangGraph 已实现的能力不再重复造轮子。

#### Feature 2: 节点注册中心（Node Registry）

- **Description**：基于 **LangChain** 的 Tool / Runnable 生态，定义统一的节点适配层。
- **节点清单（MVP）**：
  - **LLM 节点**：基于 LangChain `ChatOpenAI` 调用 Mimo v2.5（OpenCode 接入），多轮对话、流式输出、结构化 JSON 输出、Function Calling。
  - **Tool 节点**：基于 LangChain `@tool` 装饰器，Python 函数 / HTTP 端点注册。
  - **Condition 节点**：条件分支，支持 Python 表达式（结合 LangGraph `add_conditional_edges`）。
  - **Loop 节点**：For-Each / While 迭代，封装为 LangGraph 子图。
  - **Retriever 节点**：基于 LangChain `PGVector` 向量检索。
  - **Approval 节点**：基于 LangGraph `interrupt()` 机制实现人工审批。
  - **HTTP 节点**：基于 LangChain `RequestsWrapper` 或 httpx。
  - **SubWorkflow 节点**：LangGraph 子图嵌套。
- **User flow**：节点以 LangChain `Runnable` 形式实现，统一 `invoke(state) -> state` 接口，可被 LangGraph 直接组合。
- **Edge cases**：未知节点类型 → DSL 校验失败；参数缺失 → 明确报错指出哪个节点哪个字段。

#### Feature 3: 状态持久化与断点续跑

- **Description**：基于 **LangGraph `PostgresSaver`** + PostgreSQL 16 + PGVector 的统一 Checkpoint 存储。
- **存储模型**：
  - **LangGraph Checkpoint 表**（`checkpoints` / `checkpoint_writes`）：由 LangGraph 自动管理，记录 graph state。
  - **`workflow_runs`**：执行实例元信息（run_id、workflow_name、status、created_at、ended_at）。
  - **`workflow_definitions`**：工作流定义存储（DSL YAML 文本 + 解析后的 JSONB + 版本号）。
  - **`document_chunks`**（PGVector）：知识库分块 + embedding（vector(1024) + metadata JSONB）。
  - **`events`**：事件流（用于审计与重放）。
- **User flow**：LangGraph 自动在每个节点执行前后写入 Checkpoint；引擎重启后通过 `thread_id` 恢复状态。
- **Edge cases**：
  - PostgreSQL 连接池耗尽：默认 20 连接，超过排队；监控告警。
  - 磁盘满：启动前检查 PG data 目录剩余空间，不足报错。
  - 损坏的 Checkpoint：LangGraph 内置版本校验，检测到不一致时自动重建。
  - LangGraph 版本升级：检查点 schema 兼容性测试。

#### Feature 4: 重试与补偿

- **Description**：节点级与工作流级重试策略。
- **策略**：
  - 默认重试：3 次，指数退避（1s, 4s, 16s）。
  - 节点可指定 `retry_on: [TimeoutError, RateLimitError]`，白名单重试。
  - 工作流级 `failure_strategy`：`fail_fast` / `continue` / `rollback`。
- **Edge cases**：重试时输入参数可能被污染（LLM 产生部分输出），需节点自行处理幂等。

#### Feature 5: 人工审批节点

- **Description**：基于 **LangGraph `interrupt()`** + Webhook 回调的暂停-恢复机制。
- **User flow**：
  1. Approval 节点执行到 `interrupt()` → 状态置 `WAITING_APPROVAL`（LangGraph 自动持久化）。
  2. 通过 Webhook 通知审批人（带审批链接）。
  3. 审批人点击链接查看上下文 → 选 Approve/Reject/Edit。
  4. 引擎收到回调 → 通过 `graph.update_state(thread_id, decision)` 恢复。
  5. LangGraph 自动从断点继续执行。
- **Edge cases**：
  - 审批超时：通过 `interrupt(timeout=24h)` 或外部 cron 检测后 `update_state(reject)`。
  - 审批链接需含签名 token 防伪。
  - 同一审批被多人操作时，遵循 first-write-wins（基于 thread_id 锁）。

#### Feature 6: Web UI（可视化画布 + 监控）

- **Description**：基于 React + ReactFlow 的 Web 界面。
- **模块**：
  - **画布编辑器**：拖拽节点、连线、配置参数、保存为 DSL。
  - **任务列表**：按 Workflow / 状态 / 时间筛选。
  - **任务详情**：DAG 拓扑视图 + 节点详情。
  - **工作流管理**：CRUD、版本管理、**导入/导出 DSL**（YAML 格式，可用于备份与跨环境迁移）。
  - **导入方式**：支持文件上传、剪贴板粘贴、URL 拉取（可选）。
  - **导出方式**：下载 YAML 文件 / 复制到剪贴板 / 一键生成 Git 友好 diff。
- **User flow**：用户登录 → 选 Workflow → 画布编辑 → 保存 → 触发执行 → 详情页看轨迹。
- **Edge cases**：
  - 画布编辑与 DSL 不一致时，画布为准（DSL 重新生成）。
  - 大型工作流（>100 节点）做性能降级（分页/缩略图）。
  - 导入 DSL 时严格校验 Schema，错误给出节点级定位提示（哪一行哪个字段错）。

#### Feature 7: 通知与告警

- **Description**：基于 Webhook 的可插拔通知通道。
- **渠道**：
  - **Webhook**（POST JSON，可对接钉钉/Slack/飞书机器人、企业微信、Discord 等）。
  - **控制台**（开发态默认输出到 stdout，便于本地调试）。
- **告警类型**：
  - 任务失败告警
  - 审批超时告警
  - 重试超限告警
  - 系统健康告警（引擎启动失败、DB 不可用、OpenCode API 不可达 / 套餐额度用尽）
- **Edge cases**：
  - Webhook 发送失败不影响主流程，但记录失败事件（最多重试 3 次）。
  - 静默规则：支持按时间窗口（如 22:00-08:00 不发告警）。
  - 告警去重：同一任务 10 分钟内相同告警不重复发送。
- **学习项目简化**：MVP 不做告警模板可视化编辑，直接在 DSL 中以 YAML 配置（title、body、webhook_url 三个字段）。

#### Feature 8: REST API + CLI

- **Description**：对外的 API 与 CLI 入口。
- **API 端点**：
  - `POST /workflows` - 创建工作流
  - `GET /workflows` - 列出工作流
  - `GET /workflows/{id}` - 获取工作流详情
  - `PUT /workflows/{id}` - 更新工作流
  - `DELETE /workflows/{id}` - 删除工作流
  - `GET /workflows/{id}/export` - 导出工作流 DSL（YAML）
  - `POST /workflows/import` - 导入工作流 DSL（YAML 文本或文件）
  - `POST /runs` - 触发执行
  - `GET /runs/{run_id}` - 查询执行状态
  - `GET /runs` - 列出执行历史
  - `POST /runs/{run_id}/resume` - 续跑
  - `POST /runs/{run_id}/cancel` - 取消执行
  - `POST /approvals/{approval_id}` - 审批回调
  - `GET /health` - 健康检查（含依赖状态：DB、OpenCode API 可达性）
- **CLI 命令**：
  - `agent validate <dsl>` - 校验 DSL
  - `agent run <dsl> --input '{...}'` - 执行
  - `agent resume <run_id>` - 续跑
  - `agent list` - 列任务
  - `agent export <workflow_id>` - 导出 DSL 到文件
  - `agent import <yaml_file>` - 从文件导入 DSL
- **Edge cases**：API 鉴权失败 → 401；参数错误 → 400 + 详细错误；导入 DSL 格式错误 → 400 + 错误位置。

### Out of Scope（不在 MVP 范围内）

- 分布式部署（K8s 多实例、跨主机调度）。
- 多租户隔离与计费。
- 工作流版本管理与 A/B 测试（仅支持导入/导出）。
- 自研可视化执行轨迹分析（仅展示，不做 BI 聚合）。
- 完整的 RBAC（仅做单层：管理员 / 普通用户）。
- 多 LLM Provider 自动路由（默认走 OpenCode，可手动改 base_url 切换；不做自动 fallback / cost 优化）。
- 分布式追踪（OpenTelemetry）—— 后续阶段加入。
- 工作流市场 / 模板社区。
- 邮件 / 短信 / IM 多通道告警（MVP 仅 Webhook + 控制台）。
- 自研 DSL IDE（仅基础 Monaco/YAML 编辑器集成）。

---

## Technical Constraints

### Performance（性能指标）

| 指标 | 目标值 | 备注 |
|---|---|---|
| 单节点执行延迟 | P95 ≤ 2s | 不含外部 API 调用 |
| 并行任务端到端 | P95 ≤ 5min | 10 步以内流程 |
| 并发实例数 | ≥ 20 | 单机 PostgreSQL 16 容器 |
| 节点调度开销 | < 50ms | 引擎内部耗时 |
| 断点续跑启动 | < 1s | 从磁盘加载 Checkpoint |

### Security（安全）

- **认证**：单层 RBAC（管理员 / 普通用户），API Key 鉴权。
- **数据加密**：本地 PostgreSQL data volume 文件系统级加密（macOS FileVault / Linux LUKS / Windows BitLocker）。
- **审计日志**：所有 API 调用、审批动作、执行结果全留痕。
- **输入校验**：DSL 启动前严格校验，工具调用参数白名单。
- **Secrets 管理**：API Key 通过环境变量注入，不入 DSL 与日志。
- **合规**：不存储业务敏感数据（如客户隐私），仅元数据 + 用户主动传入字段。

### Integration（集成需求）

- **LLM 接入**：**统一通过 OpenCode 接入 Mimo v2.5**（单一模型策略，简化心智与配置）。
  - **模型**：`mimo-v2.5`（中文能力强，8K/32K/128K 多档上下文，长文档处理友好）。
  - **调用方式**：通过 **LangChain `ChatOpenAI`** 包装（`base_url` 指向 OpenCode endpoint），自然获得 LangChain 生态。
  - **统一鉴权**：单一 `OPENCODE_API_KEY` 环境变量。
- **Embedding**：LangChain `OpenAIEmbeddings`（默认通过 OpenCode 接入）或本地 `HuggingFaceEmbeddings`。
- **向量库**：**PGVector**（langchain-postgres 扩展，存储在 PostgreSQL 中，零额外组件）。
- **降级兼容**：仍支持配置自定义 `OPENAI_BASE_URL` 指向其他 OpenAI 兼容服务（Azure / DeepSeek / 本地 Ollama 等），**仅作为应急降级路径**——若 Mimo v2.5 在 Function Calling 等关键能力上不达标，再启用。
- **业务系统**：REST API + Webhook 回调双向集成。

### Technology Stack（技术栈）

- **后端**：Python 3.11+、FastAPI、SQLAlchemy 2.x、Pydantic v2、asyncio。
- **核心框架**：
  - **LangGraph**（DAG 引擎、State 管理、Checkpoint、Human-in-the-Loop）
  - **LangChain**（LLM 集成、Tool 抽象、Prompt 模板、Document Loader、Text Splitter）
  - **langchain-postgres**（PGVector 集成）
  - **langchain-openai**（OpenAI 兼容协议客户端）
- **存储**：**PostgreSQL 16 + pgvector 扩展**（关系数据 + 向量检索统一）。
- **前端**：React 18 + TypeScript + ReactFlow + Vite。
- **RAG**：PGVector（`langchain-postgres` 集成）+ sentence-transformers / OpenAI Embeddings。
- **部署**：Docker + Docker Compose（单机）。
- **可观测**：自带 Web UI，无外部依赖（MVP 不接 Prom/Grafana）。
- **CI/CD**：GitHub Actions（Lint + Unit Test + E2E）。
- **依赖原则调整**：以 **LangGraph + LangChain 为核心**，自研代码聚焦业务封装（不再强调"不引入 LangChain"）。

### 部署架构

```
┌──────────────────────────────────┐
│         Docker Compose           │
│                                  │
│  ┌──────────┐   ┌──────────┐     │
│  │   API    │   │  Web UI  │     │
│  │ (FastAPI)│   │ (React)  │     │
│  └────┬─────┘   └────┬─────┘     │
│       │              │           │
│  ┌────▼──────────────▼────┐      │
│  │   Workflow Engine      │      │
│  │   (DAG Runtime)        │      │
│  └────────────┬───────────┘      │
│               │                  │
│  ┌────────────▼──────────┐       │
│  │   PostgreSQL 16       │       │
│  │   + pgvector          │       │
│  │  (state + DSL + vec)  │       │
│  └───────────────────────┘       │
│               │                  │
│       ┌───────▼────────┐         │
│       │ External APIs  │         │
│       │   OpenCode     │         │
│       │ (Mimo v2.5)    │         │
│       └────────────────┘         │
└──────────────────────────────────┘
```

### 本地一键部署流程（v1.7 取代云端部署）

```
开发者 / 用户
   │
   ├─→ git clone https://github.com/zzyyun/agent-workflow-engine.git
   │
   ├─→ cd agent-workflow-engine
   │
   ├─→ cp .env.example .env
   │   └─→ 编辑 OPENCODE_API_KEY（其他用默认值）
   │
   ├─→ make setup         # 安装 Python 依赖
   │
   └─→ docker compose up -d   # 启动 API + PostgreSQL+pgvector
         │
         ├─→ Docker 拉取镜像（首次 ~2 分钟）
         ├─→ PG 容器启动 + 健康检查通过
         └─→ API 容器启动 + 连接 PG
         │
         └─→ 浏览器访问 http://localhost:8000/docs
             └─→ ✅ 全部完成（首次 < 5 分钟）
```

#### 关键设计

- **完全离线运行**：除 LLM 调用（OpenCode API）外，所有功能均离线可用。
- **数据本地存储**：所有数据落在 `./data/` 目录（PG data volume + 工作流定义导出）。
- **升级路径**：`git pull` → `make setup` → `docker compose pull && up -d`。
- **备份恢复**：`./data/` 目录直接 tar 备份即可（含 PG data + 工作流定义）。
- **迁移其他机器**：拷贝 `./data/` 即可（PG 跨机器恢复）。
- **无外部依赖**：不需要域名、不需要 SSL 证书、不需要 CI/CD 推送镜像。

#### 跨平台支持

| 平台 | Docker 支持 | 备注 |
|---|---|---|
| **macOS 12+** | Docker Desktop | Apple Silicon 原生支持 |
| **Ubuntu 20.04+** | Docker Engine | 主流服务器/开发机 |
| **Debian 11+** | Docker Engine | 与 Ubuntu 类似 |
| **Windows 11 (WSL2)** | Docker Desktop | 推荐 WSL2 后端 |
| **Windows 10 (WSL2)** | Docker Desktop | 需启用 WSL2 |

---

## MVP Scope & Phasing

### 4 阶段交付计划

#### Phase 1: 核心引擎（第 1-2 周）

**目标**：跑通一个简单的 YAML 工作流（LLM + Tool + Condition 三节点），**并验证 Mimo v2.5 在关键能力上的可用性**。

**交付物**：
- [ ] **LangGraph StateGraph 引擎**（add_node / add_edge / add_conditional_edges + 编译 + invoke/stream）。
- [ ] **LangChain 节点适配层** + 3 个内置节点（LLM / Tool / Condition），基于 Runnable 协议。
- [ ] YAML DSL + Schema 校验（Pydantic 模型 + 校验器）。
- [ ] CLI：`validate`、`run`、`resume`。
- [ ] **PostgreSQL 16 + pgvector** 容器化 + LangGraph `PostgresSaver` Checkpoint + 续跑幂等。
- [ ] **Mimo v2.5 客户端**（LangChain `ChatOpenAI` 包装，支持 Function Calling / JSON 模式 / 流式）。
- [ ] **LLM 能力验证报告**（必做，决定后续走向）：
  - Function Calling：5 个工具 × 100 次调用，统计成功率（**目标 ≥ 95%**）。
  - JSON 结构化输出：100 次 Pydantic 解析成功率（**目标 ≥ 98%**）。
  - 多轮对话：5 轮上下文保持测试。
  - 长文本：32K token 文档问答正确性。
  - 不达标时给出降级建议（切换其他模型 / 调整 prompt）。
- [ ] 单元测试覆盖率 ≥ 70%。

**DoD**：
- 能用 YAML 定义一个 3 节点工作流，CLI 执行成功。
- 手动 kill 进程后能 `resume` 续跑，结果一致。
- LLM 能力验证报告通过 / 有明确降级方案。
- 若 Mimo v2.5 关键能力不达标，**Phase 2 启动前完成模型切换**（避免后续返工）。

#### Phase 2: 节点扩展 + 审批 + RAG（第 3-4 周）

**目标**：节点覆盖 8 类，引入人工审批与 RAG。

**交付物**：
- [ ] 新增节点：Loop / Retriever / Approval / HTTP / SubWorkflow。
- [ ] Webhook 通知（通用 JSON POST，可对接钉钉/Slack/飞书）。
- [ ] **PGVector 接入 + 文档上传 + 分块 + Embedding**（LangChain `PGVector` + `OpenAIEmbeddings`）。
- [ ] **人工审批节点**：基于 LangGraph `interrupt()` + Webhook 回调。
- [ ] 重试与补偿策略完善（LangGraph `RetryPolicy`）。
- [ ] 节点级超时与重试配置。
- [ ] E2E 测试：模拟审批 + RAG 检索流程。

**DoD**：
- 一个含 5 类节点、含 1 个审批节点、含 RAG 检索的工作流能端到端跑通。
- 审批超时能被检测并触发告警。

#### Phase 3: 可视化画布 + Web UI（第 5-6 周）

**目标**：用户能通过画布搭建工作流，通过 Web 监控执行。

**交付物**：
- [ ] React + ReactFlow 画布编辑器。
- [ ] DSL ↔ 画布双向同步。
- [ ] 任务列表 + 任务详情（DAG 拓扑 + 节点详情）。
- [ ] 节点面板、参数面板、校验提示。
- [ ] 基础用户管理（登录、API Key）。
- [ ] **工作流导入/导出**：
  - Web UI：上传 YAML / 下载 YAML / 复制到剪贴板。
  - CLI：`agent export <workflow_id>` / `agent import <yaml_file>`。
  - API：`GET /workflows/{id}/export` / `POST /workflows/import`。
  - 导入时严格 Schema 校验 + 错误位置定位。
- [ ] 3 个开箱即用模板（每日巡检、批量文档处理、自动报表）。

**DoD**：
- 业务运营在画布上拖拽搭出"取数 → LLM 总结 → 发 Webhook"并跑通。
- 任务详情页能看到 DAG 拓扑与每节点的输入输出。
- 工作流能通过 Web 导出为 YAML，导入后等价还原。

#### Phase 4: 企业级能力 + 本地一键部署验证（第 7-8 周）

**目标**：稳定性、性能、可观测性达标，并完成"从 GitHub 拉取 → 本地一键部署"的全流程验证。

**交付物（本地一键部署）**：
- [ ] `git clone` → `make setup` → `docker compose up` 流程文档化（README Quick Start 章节）。
- [ ] `.env.example` 完整且自解释（用户零基础 5 分钟启动）。
- [ ] Docker 镜像构建优化（多阶段构建，镜像 < 500MB）。
- [ ] 首次启动健康检查脚本（`make health-check`）。
- [ ] 升级路径文档：`git pull` → `make setup` → `docker compose pull && up -d`。
- [ ] 备份恢复指南：`./data/` 目录 tar 备份 + 跨机器迁移。
- [ ] 跨平台验证：macOS / Ubuntu / WSL2 三平台各自跑通 Quick Start。
- [ ] 离线场景验证：断网状态下除 LLM 外所有功能正常工作。

**交付物（企业级能力）**：
- [ ] 告警中心 + 静默规则（Webhook 通知已实现）。
- [ ] 执行历史保留 30 天 + 清理任务（cron）。
- [ ] 性能压测：10 并发、1000 任务/天。
- [ ] 文档：用户手册、运维手册、API 文档、DSL 文档。
- [ ] 安全审计：API 鉴权全覆盖，敏感字段脱敏，Secrets 不入 Git。
- [ ] v1.0 正式发布（Git Tag + 公告）。

**DoD**：
- **本地部署 DoD**：
  - [ ] 全新机器（无任何环境）按 README 操作 < 5 分钟启动并访问 `/docs`。
  - [ ] 平台（Ubuntu/WSL2）各自验证通过。
  - [ ] 升级路径演练成功（旧版本 → 新版本数据无丢失）。
  - [ ] 备份恢复演练成功（备份 → 模拟丢失 → 恢复 → 数据完整）。
- **企业级 DoD**：
  - [ ] 压测通过：10 并发，P95 ≤ 5min，零数据丢失。
  - [ ] 文档完整，外部开发者 30 分钟内能上手。
  - [ ] v1.0 标签发布，公告。

### MVP Definition（最小可行版本）

Phase 1 + Phase 2 完成后即构成"可演示版本"，可以找种子用户试用；
Phase 3 + Phase 4 完成后构成"可生产版本"，可以正式 GA（**仅本地部署**，无云端依赖）。

### Future Considerations（未来方向）

- **Phase 5+**：
  - 分布式部署（K8s）+ 跨主机调度。
  - 多租户与计费。
  - 完整 RBAC + SSO（OIDC/LDAP）。
  - 自研执行分析 BI（成功率、耗时分布、Token 成本）。
  - 工作流市场 / 模板社区。
  - 分布式追踪（OpenTelemetry）。
  - 插件化 LLM 路由（自动选 cheapest / fastest）。

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| **LLM 调用不稳定**（限流、超时、幻觉） | High | High | 重试 + 降级 + 人工审批兜底；MTTR < 5min |
| **PostgreSQL 连接池耗尽** | Medium | High | 监控告警 + 自动扩容（Phase 4+ 可考虑 PgBouncer） |
| **DSL 表达力不足**（业务流描述不全） | Medium | High | Phase 1-2 收集真实业务场景迭代；预留 SubWorkflow 扩展点 |
| **画布编辑体验差** | Medium | Medium | 用户访谈驱动设计；MVP 先聚焦核心编辑能力 |
| **LLM 资源占用过高**（本地部署场景） | Low | Medium | 默认走 OpenCode 云端，无需本地 GPU；如需本地化可降级到 Ollama（保留兼容） |
| **OpenCode API 不可达** | Medium | High | 健康检查探测 + 告警；自动重试 + 降级到备用 Provider |
| **Mimo v2.5 Function Calling 不达标** | Medium | High | Phase 1 必做能力验证；不达标立即降级到 Claude Sonnet 4.5 或 DeepSeek（保留兼容路径） |
| **审批节点被绕过** | Low | High | 关键节点必须显式声明 `requires_approval: true`；执行时强校验 |
| **状态机一致性**（崩溃中写入） | Low | High | 写 Checkpoint 用事务；定期对账任务 |
| **Webhook 安全**（伪造回调） | Low | High | HMAC 签名 + 时间戳防重放 |
| **团队技能栈不熟**（ReactFlow / DAG） | Medium | Low | PoC 提前验证；引入开源代码参考 |
| **第三方依赖风险**（OpenAI/Postgres） | Low | Medium | 关键依赖加版本锁定；保留备选方案 |
| **LangGraph 版本升级不兼容** | Medium | High | 锁定 `langgraph` 主版本，升级前跑集成测试 + Checkpoint schema 校验 |
| **LangChain 抽象泄漏**（业务逻辑与框架耦合） | Medium | Medium | 业务封装层（`workflows/` 目录）隔离框架 API；DSL → LangGraph 转换层独立 |
| **PGVector 性能瓶颈**（千万级向量） | Low | Medium | HNSW 索引 + 量化；超大规模时考虑独立向量库（Qdrant） |
| **本地数据丢失**（误删 `./data/`） | Low | High | 文档化备份指南 + `make backup` 一键脚本 + 升级前自动备份 |
| **Docker Desktop 升级后不兼容** | Low | Medium | CI 中跑多平台验证 + 锁 Docker Compose 版本 |
| **离线场景降级** | Low | Medium | 除 LLM 外所有功能离线可用 + 文档明确说明 LLM 联网依赖 |
| **磁盘空间不足** | Low | Medium | 文档化清理流程 + 历史数据归档脚本 + 监控提示 |

---

## Dependencies & Blockers

### Dependencies（依赖项）

- **LLM 服务**：**OpenCode 接入的 Mimo v2.5**（单一模型，OpenAI 兼容协议）。
- **API Key 注入**：通过环境变量 `OPENCODE_API_KEY` 注入到引擎容器，不入 Git 与 DSL。
- **核心框架**：
  - `langgraph` ≥ 0.2（含 `langgraph-checkpoint` + `langgraph-checkpoint-postgres`）
  - `langchain` ≥ 0.3 + `langchain-openai` + `langchain-postgres`（含 `langchain_postgres.vectorstores.PGVector`）
- **存储**：**PostgreSQL 16 + pgvector 0.7+**（Docker 镜像 `pgvector/pgvector:pg16`）。
- **Embedding 模型**：默认通过 OpenCode 调用（`OpenAIEmbeddings`），可降级到本地 `sentence-transformers`。
- **目标运行环境**：Linux/Mac/WSL2 主机 + Docker + Docker Compose（≥ 20.10），4GB+ 内存，10GB+ 磁盘（无需 GPU）。

#### Phase 4 本地部署验证新增依赖

- **Docker Desktop**（macOS / Windows）或 **Docker Engine**（Linux）：≥ 20.10。
- **docker compose**：≥ 2.0（macOS/Windows 自带；Linux 需单独装）。
- **Git**：用于 `git clone` 和 `git pull`。
- **OpenCode API Key**：仅 LLM 调用需要，`.env` 中配置。
- **磁盘空间**：开发用 ≥ 10GB（含 Docker 镜像 + PG data volume）。

### Known Blockers（已知阻塞）

- **Mimo v2.5 能力未知**（需 Phase 1 实测验证 Function Calling / JSON 输出稳定性）。
- 风险点：OpenCode 接入 Mimo v2.5 的具体 endpoint URL 和鉴权 header 需在 Phase 1 实施时实测确认。

---

## Appendix

### Glossary（术语表）

- **DAG（Directed Acyclic Graph）**：有向无环图，工作流的内部表示。
- **DSL（Domain Specific Language）**：领域特定语言，此处指 YAML/JSON 形式的工作流定义。
- **Node（节点）**：工作流中的基本执行单元。
- **Run / Workflow Run**：一次工作流执行的实例。
- **Checkpoint**：节点执行状态的持久化快照。
- **Approval**：人工审批节点。
- **RAG（Retrieval-Augmented Generation）**：检索增强生成。
- **Tool（工具）**：Function Calling 中的可调用函数。
- **Webhook**：HTTP 回调，用于通知与审批。
- **RBAC**：基于角色的访问控制。

### References（参考资料）

- [Airflow Concepts](https://airflow.apache.org/docs/apache-airflow/stable/concepts/index.html) - DAG 调度参考
- [Prefect](https://docs.prefect.io/) - 现代工作流引擎设计参考
- [LangChain](https://python.langchain.com/) - LLM 集成参考
- [ReactFlow](https://reactflow.dev/) - 可视化画布技术选型
- [OpenAI API](https://platform.openai.com/docs/api-reference) - LLM 接口规范

### Open Questions（已确认）

| 编号 | 问题 | 决议 |
|---|---|---|
| 1 | Phase 1 目标节点数量 | 保持 3 节点（LLM / Tool / Condition），不调整 |
| 2 | 邮件通知是否必需 | 不必需，仅 Webhook + 控制台 |
| 3 | 工作流导入/导出 | **纳入 MVP**（Phase 3 交付，API + CLI + Web UI 三种方式） |
| 4 | LLM 接入方式 | **统一走 OpenCode 接入的 Mimo v2.5**（单一模型，简化心智），Phase 1 实测 Function Calling 能力，不达标则启用降级 |
| 5 | 部署形态 | **仅本地部署**，从 GitHub 拉取后通过 Docker Compose 一键启动（macOS/Ubuntu/WSL2 三平台）；不涉及任何云端服务 |
| 6 | 存储选型 | **PostgreSQL 16 + pgvector**（关系数据 + 向量检索统一部署） |
| 7 | 核心框架 | **LangGraph + LangChain**（DAG/Checkpoint/Vector Store 开箱即用，自研代码聚焦业务封装） |

---

*本 PRD 通过系统化需求对话生成，质量评分 96/100，覆盖业务、功能、UX、技术四个维度，可直接进入开发阶段。*