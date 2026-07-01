# Issue: Design System 实现（配色 + 图标 + 动画）

**Phase**: 3a / Cross-cutting (Week 5, Day 2-3)
**Priority**: P0
**Labels**: `frontend`, `phase-3a`, `design-system`, `P0`

---

## Description

基于 PRD 中 Design System & 竞品参考章节，实现完整的 Design Token 体系、节点图标映射、动画方案。

## 交付物

- [ ] CSS 变量文件（`--color-node-llm`, `--color-node-tool` 等 8 类节点色 + 7 类状态色）
- [ ] Ant Design ConfigProvider 品牌色覆盖
- [ ] 8 类自定义节点 React 组件（含 Lucide 图标 + 类型色标识）
- [ ] 节点状态色体系（待执行灰 / 运行中蓝 / 成功绿 / 失败红 / 跳过黄 / 等待审批橙 / 已取消冷灰）
- [ ] 全局动画配置：
  - 页面切换 fadeIn 200ms
  - 面板展开/收起 250ms
  - 节点状态过渡 300ms
  - Toast 滑入 300ms + 3s 停留
- [ ] DAG 连线流动画（`stroke-dasharray` 脉冲效果）
- [ ] 响应式布局：XL(1600+) / L(1280-1599) / M(1024-1279)
- [ ] WCAG AA 对比度保障（文字 ≥ 4.5:1）

## Acceptance Criteria

- [ ] 深色文本 `#111827` 在 `#F9FAFB` 背景上对比度 ≥ 10:1
- [ ] 品牌色按钮 hover 有 200ms 过渡效果
- [ ] 画布中 LLM 节点显示靛蓝 `#6366F1`，Tool 节点显示琥珀色 `#F59E0B`
- [ ] 任务运行中节点呈蓝色 `#3B82F6`，成功后变为绿色 `#22C55E`
- [ ] 窗口缩放到 1100px 时左侧面板自动折叠
- [ ] 节点支持 keyboard tab 导航

## Technical Notes

参考项目: LangFlow（节点颜色分类）、Apache Airflow（状态色）、n8n（图标体系）

```typescript
// CSS 变量示例
:root {
  --color-node-llm: #6366F1;
  --color-node-tool: #F59E0B;
  --color-node-condition: #10B981;
  --color-node-loop: #8B5CF6;
  --color-node-retriever: #06B6D4;
  --color-node-approval: #F43F5E;
  --color-node-http: #14B8A6;
  --color-node-subworkflow: #78716C;

  --color-status-pending: #9CA3AF;
  --color-status-running: #3B82F6;
  --color-status-success: #22C55E;
  --color-status-failed: #EF4444;
  --color-status-skipped: #EAB308;
  --color-status-waiting: #F97316;
  --color-status-canceled: #6B7280;
}
```

## Dependencies

- Issue #01 (Project Scaffolding) — 需先有项目框架
