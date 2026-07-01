# Issue: 重跑/续跑 + 任务取消

**Phase**: 3c (Week 6, Day 4)
**Priority**: P1
**Labels**: `frontend`, `phase-3c`, `retry`, `P1`

---

## Description

实现任务重跑能力：允许用户重跑整个失败任务，或从指定失败节点重跑；以及在任务运行中取消任务。

## 交付物

- [ ] 任务详情页「重跑整个任务」按钮（失败/已完成的任务）
- [ ] 任务详情页节点详情面板「从该节点重跑」按钮（失败节点）
- [ ] 重跑确认弹窗（提示「重跑将产生新的执行记录」）
- [ ] 任务列表页每行「重跑」快捷按钮
- [ ] 运行中任务「取消任务」按钮 + 二次确认
- [ ] 取消后任务状态变为「已取消」

## Acceptance Criteria

- [ ] 失败任务点击「重跑整个任务」→ 确认 → 跳转到新的任务详情页
- [ ] 点击「从该节点重跑」→ 新任务跳转详情页，执行从该节点开始
- [ ] 运行中任务点击「取消」→ 确认 → 任务状态变为已取消
- [ ] 取消后不可继续操作该任务

## API Contract

```typescript
POST /api/runs/:runId/retry
Response: { newRunId: string }

POST /api/runs/:runId/retry-from/:nodeId
Response: { newRunId: string }

POST /api/runs/:runId/cancel
Response: { status: 'canceled' }
```

## Dependencies

- Issue #09 (Task Detail Page)
- 后端 API: 重跑 + 取消接口
