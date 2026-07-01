# Issue: 模板市场页

**Phase**: 3d (Week 6, Day 5)
**Priority**: P2
**Labels**: `frontend`, `phase-3d`, `templates`, `P2`

---

## Description

实现模板市场页：展示预置工作流模板，一键创建并跳转编辑。

## 交付物

- [ ] 模板市场页（`/templates`）：
  - 卡片网格展示（3 列响应式）
  - 每张卡片包含：模板名称、简短描述、节点数量、预计完成时间、标签
  - 模板分类标签（业务类 / 技术类 / 入门教程）
- [ ] 点击卡片 → 详情弹窗（含预览 DAG 缩略图 + 完整描述）
- [ ] 「使用模板」按钮 → API 创建 → 跳转画布编辑器
- [ ] 3 个 MVP 模板配置（预置 YAML）：
  1. **每日巡检报表**: 检索数据 → LLM 分析 → Markdown 报告 → Webhook 通知
  2. **批量文档处理**: 读取文档列表 → Loop 每个文档 → LLM 提取摘要 → 汇总保存
  3. **自动报表生成**: 查询数据库 → LLM 分析趋势 → 生成图表描述 → 邮件通知

## Acceptance Criteria

- [ ] 模板市场页展示 3 个模板卡片，正确显示名称和描述
- [ ] 点击「每日巡检报表」卡片 → 详情弹窗 → 点击「使用模板」→ 创建成功并跳转编辑器
- [ ] 画布中已包含预置节点和连线
- [ ] 基于模板创建的工作流可自由编辑和删除
- [ ] 模板本身不可在 UI 中编辑（只读）

## API Contract

```typescript
GET /api/templates
Response: {
  items: Template[]
}

type Template = {
  id: string
  name: string
  description: string
  category: 'business' | 'technical' | 'tutorial'
  nodeCount: number
  estimatedTime: string
  tags: string[]
  previewYaml?: string
}

POST /api/templates/:id/use
Response: { workflowId: string, workflowName: string }
```

## Dependencies

- Issue #05 (Canvas Editor Core) — 创建后跳转编辑
- 后端 API: 模板列表 + 模板使用接口
- 3 个预置模板的 YAML 定义
