# Issue: 边缘情况处理（空状态 + 错误边界 + 全局异常）

**Phase**: 3d (Week 6, Day 5)
**Priority**: P2
**Labels**: `frontend`, `phase-3d`, `polish`, `P2`

---

## Description

实现所有页面的空状态、错误边界、全局异常处理和加载态，完善用户体验的最后一公里。

## 交付物

- [ ] React Error Boundary 组件（全局，捕获渲染异常并显示友好界面 + 刷新按钮）
- [ ] 所有页面 Loading Skeleton（内容加载中骨架屏）
- [ ] 全局 Toast 通知系统（Ant Design `message` / `notification`）
- [ ] 空状态组件（插画 + 文案 + 操作引导按钮）：
  - 工作流列表空态：「还没有工作流，开始创建第一个」
  - 任务列表空态：「还没有执行记录，触发一个工作流试试」
  - 搜索结果空态：「没有找到匹配的工作流」
  - 模板市场空态（模板加载失败兜底）
- [ ] API 请求异常统一处理：
  - 400: 显示后端返回的详细错误信息
  - 401: 自动跳转登录页
  - 403: Toast「无权限操作」
  - 404: 显示 404 页面
  - 500: Toast「服务器异常，请稍后重试」
  - 网络超时: Toast「请求超时，请检查网络连接」
- [ ] 全页面 404 兜底组件
- [ ] 页面标题随路由变化（`document.title` 动态更新）

## Acceptance Criteria

- [ ] 清空所有工作流，列表页显示空状态插画 +「开始创建」按钮
- [ ] 模拟 API 500 响应，全局 Toast 显示「服务器异常」
- [ ] 访问不存在的路由 `/xyz`，展示 404 页面
- [ ] 网络断开时调用 API，Toast 显示「请求超时」
- [ ] 页面切换时浏览器标题正确更新

## 组件接口

```typescript
// ErrorBoundary
<ErrorBoundary fallback={<ErrorFallback onRetry={() => window.location.reload()} />}>
  <App />
</ErrorBoundary>

// EmptyState
<EmptyState
  icon={InboxIcon}
  title="还没有工作流"
  description="开始创建第一个工作流来体验 AI 自动化能力"
  action={<Button>创建新工作流</Button>}
/>

// PageTitle
// 在路由配置中自动设置
{ path: '/workflows', title: '工作流管理 - Agent Workflow Engine' }
```

## Dependencies

- Issues #04, #08, #10 (所有页面组件需先存在)
