# Issue: 任务触发 + 任务列表页

**Phase**: 3c (Week 6, Day 3)
**Priority**: P1
**Labels**: `frontend`, `phase-3c`, `tasks`, `P1`

---

## Description

实现工作流触发执行功能（带参数输入弹窗）和任务列表页（多维筛选 + 分页）。

## 交付物

- [ ] 画布工具栏「触发执行」按钮
- [ ] 触发执行弹窗：
  - 输入参数 JSON 编辑器
  - 「执行」按钮 → 跳转任务详情页
  - 「取消」按钮
- [ ] 工作流列表页每行「触发执行」快捷按钮（同上弹窗）
- [ ] 任务列表页（`/runs`）：
  - 列表展示：任务 ID（前 8 位）、工作流名称、状态标签、触发时间、耗时
  - 状态标签带色：运行中(蓝) / 成功(绿) / 失败(红) / 等待审批(橙)
  - 筛选：按状态、按工作流名称、按时间范围（1h / 今天 / 7天 / 自定义）
  - 排序：默认按创建时间倒序
  - 每行点击跳转任务详情页
  - 「刷新」按钮（手动拉取最新数据）
- [ ] 列表分页（每页 20 条）

## Acceptance Criteria

- [ ] 从画布点击「触发执行」→ 弹窗 → 输入 JSON → 确认 → 跳转任务详情页
- [ ] 任务列表页展示最近 20 条任务，状态标签正确着色
- [ ] 按「失败」筛选后仅显示失败任务
- [ ] 时间筛选项「过去 1 小时」正确过滤
- [ ] 空列表时显示「暂无执行记录」提示

## API Contract

```typescript
POST   /api/runs
Body:  { workflowId: string, input?: Record<string, any> }
Response: { runId: string, status: string }

GET    /api/runs?workflowId=&status=&from=&to=&page=&size=
Response: {
  items: RunItem[],
  total: number,
  page: number
}

type RunItem = {
  runId: string        // 完整 ID
  shortId: string      // 前 8 位
  workflowName: string
  status: 'running' | 'success' | 'failed' | 'waiting_approval' | 'canceled'
  triggerTime: string
  duration: number     // seconds
}
```

## Dependencies

- Issue #05 (Canvas Editor Core) — 触发按钮在画布工具栏中
- 后端 API: 任务触发 + 任务列表接口
