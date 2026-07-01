# Issue: 任务详情页 — DAG 拓扑 + 节点详情 + 时间轴

**Phase**: 3c (Week 6, Day 3-4)
**Priority**: P1
**Labels**: `frontend`, `phase-3c`, `task-detail`, `P1`

---

## Description

实现任务详情页：展示完整的 DAG 执行拓扑（状态着色）、节点级输入/输出详情、时间轴视图、自动轮询刷新。

## 交付物

- [ ] 顶部概览区：工作流名称、任务 ID、状态徽标、总耗时、重试次数
- [ ] DAG 拓扑图（ReactFlow 只读模式）：
  - 节点按执行状态着色（待执行灰 / 运行中蓝 / 成功绿 / 失败红 / 跳过黄 / 等待审批橙）
  - 已执行节点添加状态角标（对勾 / 叉号 / 时钟）
  - 当前活跃连线脉冲流动画
- [ ] 点击 DAG 节点 → 下方展开节点详情面板：
  - 节点名称 + 类型
  - 输入参数（JSON 格式化展示，可折叠）
  - 输出结果（JSON 格式化展示，可折叠）
  - 执行耗时
  - Token 用量（LLM 节点）
  - 错误信息（如有）
  - 重试记录列表
- [ ] 时间轴视图（Tab 切换：DAG 拓扑 / 时间轴）：
  - 按执行顺序展示节点序列
  - 每条记录：节点名 + 状态色条 + 耗时 + 点击展开详情
- [ ] 自动轮询（任务运行中时每 3 秒拉取最新状态）
- [ ] 运行中任务显示「取消任务」按钮
- [ ] 审批中任务显示「等待审批」提示卡片

## Acceptance Criteria

- [ ] 进入详情页看到 DAG 拓扑图，节点颜色正确反映执行状态
- [ ] 点击成功节点，下方展开显示输入参数和输出结果
- [ ] 失败节点显示红色 + 错误信息
- [ ] 切换到时间轴视图，看到按时间排列的节点执行记录
- [ ] 运行中任务自动刷新，节点状态从灰→蓝→绿变化
- [ ] 刷新停止后显示最终态
- [ ] 审批中任务看到橙色节点 + 审批提示卡片

## API Contract

```typescript
GET /api/runs/:runId
Response: {
  runId: string
  workflowName: string
  status: string
  totalDuration: number
  retryCount: number
  triggerTime: string
  nodes: NodeExecution[]
}

type NodeExecution = {
  nodeId: string
  nodeName: string
  nodeType: string
  status: 'pending' | 'running' | 'success' | 'failed' | 'skipped' | 'waiting_approval'
  input: Record<string, any>
  output: Record<string, any> | null
  error: string | null
  duration: number          // ms
  tokensUsed: number | null // LLM only
  retries: RetryRecord[]
  startTime: string
  endTime: string | null
}

type RetryRecord = {
  attempt: number
  error: string
  timestamp: string
}
```

## Dependencies

- Issue #08 (Task Trigger & List)
- 后端 API: 任务详情 + 节点详情接口
