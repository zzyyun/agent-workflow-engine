# Issue: 工作流列表页

**Phase**: 3a (Week 5, Day 3)
**Priority**: P0
**Labels**: `frontend`, `phase-3a`, `workflow-list`, `P0`

---

## Description

实现工作流列表页：展示所有已保存的工作流，支持搜索、筛选、CRUD 操作和 YAML 导入。

## 交付物

- [ ] 列表展示：工作流名称、节点数量、状态（已发布/草稿）、最近更新时间
- [ ] 按名称搜索、按状态筛选
- [ ] 每行操作按钮：编辑、触发执行、导出 YAML、复制、删除
- [ ] 「新建工作流」按钮 → `/editor/new`
- [ ] 「导入 YAML」按钮 → 文件选择器 → 上传 → 跳转编辑器
- [ ] 分页（每页 20 条）
- [ ] 空状态提示 + 模板入口引导
- [ ] 删除二次确认弹窗
- [ ] 排序（更新时间 / 创建时间 / 名称）

## Acceptance Criteria

- [ ] 列表默认按更新时间倒序排列
- [ ] 搜索输入 200ms 防抖
- [ ] 导入格式错误时弹窗定位错误位置
- [ ] 删除后列表刷新、计数更新
- [ ] 空列表时展示插图 + 「新建工作流」按钮
- [ ] 状态标签区分已发布（绿）和草稿（灰）

## API Contract

```typescript
GET    /api/workflows?search=&status=&page=&size=
Response: { items: Workflow[], total: number, page: number }

POST   /api/workflows
Body:  { name: string, description?: string, yaml: string }

PUT    /api/workflows/:id
Body:  { name?, description?, yaml? }

DELETE /api/workflows/:id

GET    /api/workflows/:id/export
Response: { yaml: string, filename: string }

POST   /api/workflows/import
Body:  { yaml: string }
Response: { id: string, name: string }

type Workflow = {
  id: string
  name: string
  description?: string
  nodeCount: number
  status: 'published' | 'draft'
  updatedAt: string
  createdAt: string
}
```

## Dependencies

- Issue #01 (Project Scaffolding)
- Issue #03 (API Layer)
- 后端 API: 工作流 CRUD 接口
