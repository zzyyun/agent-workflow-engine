# Issue: 画布编辑器 — 核心编辑能力

**Phase**: 3b (Week 5, Day 4-5)
**Priority**: P0
**Labels**: `frontend`, `phase-3b`, `canvas-editor`, `P0`

---

## Description

实现基于 ReactFlow 的画布编辑器核心功能：画布渲染、8 类自定义节点、左侧节点面板、拖拽创建、保存/载入、撤销/重做。

## 交付物

- [ ] ReactFlow v11 集成，画布支持 Pan + Zoom
- [ ] 8 类自定义节点组件（LLM / Tool / Condition / Loop / Retriever / Approval / HTTP / SubWorkflow）
- [ ] 左侧节点面板，按类型分组，图标 + 名称展示
- [ ] 节点拖拽到画布创建实例（自动分配 ID: `llm_1`, `tool_2`）
- [ ] 每个节点的 ReactFlow Node 渲染：
  - 类型色左上角色条
  - 图标 + 名称居中
  - 出口锚点（底部）、入口锚点（顶部）
- [ ] 选中节点高亮 + 节点信息同步到 Store
- [ ] 保存工作流（序列化为 YAML + 位置信息）
- [ ] 载入工作流（解析 YAML + 自动布局）
- [ ] Undo / Redo（操作历史栈）
- [ ] Delete / Backspace 快捷键删除选中节点
- [ ] Snap-to-grid 对齐辅助线
- [ ] 自动布局算法（dagre）

## Acceptance Criteria

- [ ] 从左侧面板拖出 3 个不同类型的节点，画布正常渲染
- [ ] 每个节点显示正确的颜色、图标、名称
- [ ] 选中节点后有高亮边框
- [ ] 保存后刷新页面，载入后位置和内容一致
- [ ] Undo 3 次后恢复到初始状态
- [ ] Delete 键删除选中节点
- [ ] 画布缩放流畅，50 节点 FPS ≥ 30

## Node Component Spec

```typescript
// 每个自定义节点接收
interface NodeData {
  label: string        // 用户可编辑的名称
  nodeType: NodeType   // 'llm' | 'tool' | 'condition' | ...
  icon: ReactNode      // Lucide icon
  color: string        // 类型色
  config: Record<string, any>  // 节点参数
}

// 输出锚点（Source）在底部
// 输入锚点（Target）在顶部
// 无输出节点隐藏 Source 锚点（如 END 节点）
```

## Technical Notes

- 使用 `react-flow-renderer` 的 `nodeTypes` 注册自定义节点
- 节点拖拽使用 ReactFlow 原生 `onConnect` + `addEdges`
- 撤销/重做使用操作历史栈（`useRef<Action[]>` + `historyIndex`）
- 自动布局使用 `dagre` 库的 `layout` 函数

## Dependencies

- Issue #01 (Project Scaffolding)
- Issue #02 (Design System — 节点图标和配色)
- Issue #03 (API Layer)
