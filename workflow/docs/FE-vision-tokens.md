# Design Vision — AI Agent Workflow Engine

## 设计概念: 工作台 (The Workshop)

画布是工作台，节点是工具，连线是走线。UI 的功能是框住这片工作区，不让任何装饰喧宾夺主。

---

## Token System（完整色值体系）

### 画布

--canvas-bg: #0F172A (深蓝底，工作台面)
--canvas-grid: #1E293B (网格线，20px 间距)
--canvas-vignette: radial-gradient(ellipse at center, transparent 60%, #00000040 100%)

### 界面壳

--shell-bg: #F8FAFC
--shell-surface: #FFFFFF
--shell-border: #E2E8F0
--text-primary: #0F172A
--text-secondary: #64748B
--text-muted: #94A3B8

### 品牌/交互

--primary: #818CF8 (靛蓝-400，浅于标准，适配深色画布)
--primary-glow: 0 0 20px #818CF840
--accent: #22D3EE (青蓝 AI 辉光)
--accent-glow: 0 0 30px #22D3EE60
--success: #34D399
--error: #FB7185
--warning: #FBBF24

### 节点色（深色画布版，亮度提升 +15%）

| Node | Dark Canvas | Light Panel |
|------|-------------|-------------|
| LLM | #818CF8 | #6366F1 |
| Tool | #FBBF24 | #F59E0B |
| Condition | #34D399 | #10B981 |
| Loop | #A78BFA | #8B5CF6 |
| Retriever | #22D3EE | #06B6D4 |
| Approval | #FB7185 | #F43F5E |
| HTTP | #2DD4BF | #14B8A6 |
| SubWorkflow | #A8A29E | #78716C |

### Typography

| Role | Font | Weight | Size |
|------|------|--------|------|
| Display | DM Sans | 500/700 | 20/24/32px |
| Body | Inter | 400/500/600 | 12/14/16px |
| Code | JetBrains Mono | 400 | 13px |

---

## Animation Physics

```typescript
const EASE_OUT_CUBIC = 'cubic-bezier(0.33, 1, 0.68, 1)'
const EASE_OUT_BOUNCE = 'cubic-bezier(0.34, 1.56, 0.64, 1)'
const EASE_IN_OUT = 'cubic-bezier(0.65, 0, 0.35, 1)'
const ELASTIC = 'cubic-bezier(0.5, 1.75, 0.5, 1)'
```

### Effect Map

| Effect | Element | Trigger | Duration | Easing |
|--------|---------|---------|----------|--------|
| 节点放置弹跳 | 节点缩放 | 拖拽放下 | 350ms | elastic |
| 节点呼吸光晕 | box-shadow 脉动 | LLM/运行中节点 | 2s loop | ease-in-out |
| 连线粒子流 | 光点沿贝塞尔线移动 | 执行中连线 | 1.5s loop | linear |
| 连线脉冲 | stroke-dashoffset | 空闲连线 hover | 800ms | ease-out |
| 面板滑入 | translateX 滑入 | 点击打开 | 250ms | ease-out-cubic |
| 节点选中涟漪 | 中心扩散圆环 | 点击节点 | 600ms | ease-out |
| 状态色过渡 | 背景色+边框色渐变 | 轮询状态变化 | 400ms | ease-in-out |
| 失败抖动 | translateX 来回 | 节点执行失败 | 300ms | ease-in-out |
| 成功光波 | 从节点向外出射光圈 | 节点执行成功 | 500ms | ease-out |
| HUD 浮现 | opacity 0-1 + translateY | 页面加载 | 400ms | ease-out-cubic |
| 空态渐入 | 节点逐次淡入 + 连线渐显 | 首次加载 | staggered 150ms | ease-out |

---

## The Flow（Signature Effect）

工作流执行时，数据沿着 DAG 边流动。光粒子表达数据流：

- count: 3-5 个/边
- size: 4-6px 圆形
- color: 上游节点色的渐变透明
- speed: 1.5s 完成整条边
- trail: 拖尾 20px 渐隐

空闲态连线保持 20% 透明度、2px 宽；hover 时高亮至 60% + 脉冲动画。

### 节点呼吸光晕（Node Breath）
LLM 节点和运行中的节点常驻一个呼吸光晕：box-shadow 在 8-20px 间脉动。

### 节点放置弹跳（Node Drop）
从 scale(0) 到 scale(1.1) 到 scale(1)，350ms 弹性曲线。

### 成功光波（Success Ripple）
节点执行成功瞬间从中心扩散一个光波环。

### 面板滑动（Panel Slide）
左右面板从边缘滑入 250ms ease-out-cubic，内容延迟 80ms渐入。

### 页面过渡（Page Transition）
旧页 fadeOut 200ms 新页 fadeIn 250ms。

### 空态动态展示（Empty State Demo）
3 个节点缓慢呼吸，连线有微光粒子流动，循环运行。

### 画布环境氛围
网格背景极缓慢视差漂移 30s 循环，画布四角极淡径向渐隐。

---

## React Implementation

```typescript
interface FlowParticle {
  path: SVGPathElement
  progress: number
  speed: number
  size: number
}
// Use requestAnimationFrame for particle animation loop
```

CSS 变量驱动所有颜色，framer-motion/@react-spring 驱动交互动画，SVG + rAF 驱动粒子系统。
