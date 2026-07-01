# Issue: API 封装层 + 登录页 + 路由守卫

**Phase**: 3a (Week 5, Day 2-3)
**Priority**: P0
**Labels**: `frontend`, `phase-3a`, `auth`, `P0`

---

## Description

实现前端 API 通信基础设施、用户登录页、路由守卫及登录态管理。

## 交付物

- [ ] axios 实例创建（baseURL: `/api`，超时 10s，请求/响应拦截器）
- [ ] Token 管理：登录成功存 localStorage，请求头 `Authorization: Bearer <token>`
- [ ] 401 统一拦截：自动清除 token 并跳转 `/login`
- [ ] Auth API：`POST /api/auth/login`
- [ ] 登录页 UI（居中卡片式 + Logo + 用户名/密码表单）
- [ ] Route Guard 组件：未登录时跳转 `/login`，已登录时不可访问 `/login`
- [ ] Auth Context（React Context）提供全局登录态
- [ ] 退出登录功能

## Acceptance Criteria

- [ ] 未登录访问 `/workflows` 自动跳转 `/login`
- [ ] 登录失败时表单显示红色错误提示
- [ ] 登录成功自动跳转至目标页（或默认到 `/workflows`）
- [ ] 退出登录清除 token 并跳回登录页
- [ ] 后端 401 时前端自动跳转登录页
- [ ] 刷新页面后登录态保持（从 localStorage 恢复 token）

## API Contract

```typescript
POST /api/auth/login
Request:  { username: string, password: string }
Response: { token: string, user: { id: string, name: string } }

GET /api/auth/me
Headers:  Authorization: Bearer <token>
Response: { id: string, name: string, role: string }
```

## Dependencies

- Issue #01 (Project Scaffolding)
- 后端 API: `POST /api/auth/login`, `GET /api/auth/me`
