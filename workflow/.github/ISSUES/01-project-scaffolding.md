# Issue: 前端项目脚手架搭建

**Phase**: 3a (Week 5, Day 1-2)
**Priority**: P0
**Labels**: `frontend`, `phase-3a`, `P0`

---

## Description

搭建前端项目的完整基础设施：Vite + React 18 + TypeScript 项目初始化、Ant Design 5.x 主题定制、路由配置、Docker 容器化。

## 交付物

- [ ] Vite + React 18 + TypeScript 5.x 项目初始化
- [ ] Ant Design 5.x 集成 + Design Token 主题定制（品牌色 `#6366F1`）
- [ ] react-router-dom v6 路由配置（8 个页面路由）
- [ ] 三栏布局组件（顶部导航栏 48px + 左侧面板 240px + 右侧可折叠面板 360px + 底部状态栏 32px）
- [ ] 底部状态栏组件（节点数 / 校验状态 / 自动保存信息 / Undo-Redo 按钮）
- [ ] Docker 多阶段构建 + Nginx SPA fallback 配置
- [ ] `vite.config.ts` 代理配置（开发环境 `/api` → 后端）
- [ ] ESLint + Prettier 代码规范配置
- [ ] 空页面 Route Guard 骨架（仅路由配置，Auth 逻辑后续实现）

## Acceptance Criteria

- [ ] `npm run dev` 可本地启动，浏览器看到带 Logo 的空白布局框架
- [ ] Ant Design 按钮颜色为品牌色 `#6366F1`
- [ ] `npm run build` 产出 `/dist` 目录
- [ ] `docker build` 成功后，Nginx 容器返回完整 SPA
- [ ] `/login`、`/workflows`、`/editor/:id` 等路由正常注册
- [ ] 底部状态栏在画布页正常渲染

## Technical Notes

参考 PRD 的 Design System 章节：

```css
/* Ant Design 主题 Token 示例 */
{
  colorPrimary: '#6366F1',
  colorBgLayout: '#F9FAFB',
  colorBorder: '#E5E7EB',
  colorTextBase: '#111827',
  colorTextSecondary: '#6B7280',
}
```

Dockerfile 使用 Nginx 多阶段构建：
- Build stage: `node:20-alpine` → `npm run build`
- Serve stage: `nginx:alpine` → copy `/dist` to `/usr/share/nginx/html`
- SPA fallback: `try_files $uri $uri/ /index.html;`

## Dependencies

- 无（独立项目初始化）
