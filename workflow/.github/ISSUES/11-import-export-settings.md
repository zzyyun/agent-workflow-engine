# Issue: 导入/导出 YAML + 设置页

**Phase**: 3d (Week 6, Day 5)
**Priority**: P2/P3
**Labels**: `frontend`, `phase-3d`, `settings`, `P2`

---

## Description

实现工作流 YAML 导入/导出功能和用户设置页（API Key 管理 + 修改密码）。

## 交付物

### YAML 导入/导出
- [ ] 工作流列表页「导入 YAML」按钮 → 文件选择器（.yaml / .yml）
- [ ] 导入时自动校验 Schema，错误时弹窗定位
- [ ] 工作流列表页每行「导出 YAML」按钮 → 下载 `.yaml` 文件
- [ ] 画布编辑器「导出 YAML」快捷操作（工具栏按钮）
- [ ] 画布编辑器「复制 YAML 到剪贴板」

### 设置页
- [ ] 设置页（`/settings`）布局：
  - 个人信息区：用户名（只读展示）
  - 修改密码表单：旧密码 + 新密码 + 确认新密码
  - API Key 管理区：当前 Key（掩码 `sk-****...****`）
  - 「生成新 Key」按钮 → 确认后展示新 Key（一次性）→ 旧 Key 失效
  - 「复制 Key 到剪贴板」按钮
  - 系统信息区：后端版本号、引擎状态
- [ ] 设置页左侧导航（个人信息 / 安全 / 系统信息）

## Acceptance Criteria

- [ ] 从工作流列表导入 YAML → 校验通过 → 跳转画布编辑器
- [ ] 导入格式错误时弹窗显示「第 X 行：具体错误原因」
- [ ] 导出 YAML 文件正确下载，再次导入后内容一致
- [ ] 设置页展示当前 API Key 掩码
- [ ] 生成新 Key 后成功复制到剪贴板
- [ ] 修改密码成功后提示并退出登录（要求重新登录）

## API Contract

```typescript
// 导入导出
POST   /api/workflows/import
Body:  { yaml: string }
Response: { id: string, name: string }

GET    /api/workflows/:id/export
Response: { yaml: string, filename: string }

// 设置
GET    /api/settings
Response: { username: string, version: string, engineStatus: string }

PUT    /api/settings/password
Body:  { oldPassword: string, newPassword: string }

GET    /api/api-keys
Response: { key: string (masked), createdAt: string }

POST   /api/api-keys
Response: { key: string (full, show once) }

DELETE /api/api-keys/:id
```

## Dependencies

- Issue #03 (API Layer)
- Issue #04 (Workflow List)
- 后端 API: 导入导出 + 设置 + API Key 接口
