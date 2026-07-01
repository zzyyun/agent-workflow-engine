# Issue: 画布编辑器 — DSL 双向同步

**Phase**: 3b (Week 6, Day 1-2)
**Priority**: P1
**Labels**: `frontend`, `phase-3b`, `canvas-editor`, `P1`

---

## Description

在画布编辑器中实现「可视化 ↔ DSL」双向同步能力：集成 Monaco Editor 提供 YAML 编辑，画布修改自动序列化为 YAML，YAML 修改后反序列化回画布。

## 交付物

- [ ] 画布顶部 Tab 切换: [可视化] [DSL]
- [ ] Monaco Editor 集成（CDN 按需加载，减少 bundle 体积）
- [ ] YAML 语法高亮 + 自动补全
- [ ] YAML Schema 校验（根据 DSL Schema 校验错误标红 + 行定位）
- [ ] 可视化 → DSL：画布操作后自动序列化（防抖 500ms）
- [ ] DSL → 可视化：编辑 YAML 后点击「应用」，解析并重新渲染画布
- [ ] 未应用修改但切换 Tab 时弹出确认对话框
- [ ] DSL 视图中有保存按钮（同时更新画布和保存到后端）
- [ ] 复制 YAML 到剪贴板按钮

## Acceptance Criteria

- [ ] 画布中有 3 个节点，切换到 DSL Tab 看到正确的 YAML 序列化
- [ ] 在 DSL 中修改节点参数，点击「应用」，回到可视化 Tab 看到节点参数已更新
- [ ] DSL 格式错误时编辑器标红 + 状态栏显示错误信息
- [ ] 双向同步 100% 等幂：画布 → DSL → 画布 前后完全一致（含坐标位置）
- [ ] 大文件（50 节点）DSL 编辑无卡顿

## DSL 序列化格式

```yaml
# 画布 DSL 输出格式（Node 含 layout 信息）
workflow:
  name: my_workflow
  description: ""
nodes:
  - id: llm_1
    type: llm
    label: AI 总结
    config:
      system_prompt: "请总结以下内容"
      model: mimo-v2.5
      temperature: 0.7
      max_tokens: 2048
    layout:
      x: 100
      y: 200
  - id: tool_2
    type: tool
    label: 发送通知
    config:
      tool: webhook_sender
      params: {}
edges:
  - source: llm_1
    target: tool_2
    label: ""
    expression: ""
```

## Dependencies

- Issue #05 (Canvas Editor Core)
- 后端 DSL Schema 文档（节点类型、参数类型映射表）
- Monaco Editor CDN URL 确认
- js-yaml 库 (v4.x)
- ajv 或 yaml-validator (Schema 校验)
