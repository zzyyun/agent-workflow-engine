# Issue: 画布编辑器 — 参数面板 + 连线校验

**Phase**: 3b (Week 5, Day 5 – Week 6, Day 1)
**Priority**: P0
**Labels**: `frontend`, `phase-3b`, `canvas-editor`, `P0`

---

## Description

实现画布编辑器的右侧参数配置面板（类型感知的动态表单）和节点连线系统（含循环依赖检测）。

## 交付物

- [ ] 右侧参数面板（Drawer 组件，选中节点时自动弹出）
  - 节点名称（可编辑 Input）
  - 节点类型（只读 Tag）
  - 类型感知参数配置表单：
    - **LLM**: System Prompt (TextArea), Model (Select), Temperature (Slider), Max Tokens (InputNumber)
    - **Tool**: Tool Select (Select), Params Mapping (JSON Editor)
    - **Condition**: Expression Input (Input with syntax highlight)
    - **Loop**: Iteration Source (Expression), Variable Name (Input), Max Iterations (InputNumber)
    - **Retriever**: Knowledge Base (Select), TopK (InputNumber), Score Threshold (Slider)
    - **Approval**: Approver (Input), Timeout (InputNumber), Message Template (TextArea)
    - **HTTP**: URL, Method (Select), Headers (KV Editor), Body (TextArea)
    - **SubWorkflow**: Workflow Select (Select), Input Mapping (JSON Editor)
- [ ] 重试策略子面板（可折叠）：
  - 最大重试次数 (InputNumber)
  - 重试间隔秒数 (InputNumber)
  - 重试条件 (Select multiple / Tag input)
- [ ] 节点连线系统：
  - 鼠标 hover 节点显示出口/入口锚点（圆形，与节点色一致）
  - 从出口拖出贝塞尔虚线预览
  - 拖到入口锚点时高亮 + 吸附
  - 循环依赖检测（创建连线后校验）
  - 连线成功后添加微动效（涟漪）
- [ ] 选中连线后在右侧面板显示连线配置（条件边可编辑表达式）

## Acceptance Criteria

- [ ] 选中 LLM 节点，右侧面板显示 System Prompt 文本域 + Model 下拉 + Temperature 滑块
- [ ] 选中 Tool 节点，右侧面板显示工具选择下拉 + 参数映射 JSON 编辑器
- [ ] 节点间拖线成功，贝塞尔曲线正常渲染
- [ ] 尝试创建环（A→B→C→A）时阻止并提示
- [ ] Condition 节点的出站连线显示「True」「False」标签
- [ ] 修改参数后画布节点响应式更新
- [ ] 参数填写不完整时保存校验失败并提示

## Form Schema Spec

```typescript
// 每种节点类型定义自己的配置 schema
interface NodeConfigSchema {
  nodeType: NodeType
  fields: FormField[]
}

interface FormField {
  key: string
  label: string
  type: 'text' | 'textarea' | 'number' | 'slider' | 'select' | 'json' | 'kv'
  required: boolean
  defaultValue?: any
  options?: { label: string; value: string }[]  // for 'select'
  validation?: (value: any) => string | null    // return error msg or null
}
```

## Dependencies

- Issue #05 (Canvas Editor Core)
- 后端 DSL Schema 定义（8 类节点的参数 Schema）
