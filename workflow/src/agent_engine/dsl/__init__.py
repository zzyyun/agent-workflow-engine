"""YAML DSL 模块。

Phase 1.3 (Issue #7) 交付物：
- Pydantic 模型定义工作流结构
- YAML 加载与基础校验
- 节点类型白名单校验
- 引用完整性校验（依赖、边、入口、出口）
- DSL 错误信息精准定位（节点 ID + 字段名）

本模块不负责执行工作流（仅做定义与校验），
``WorkflowEngine`` 集成由 CLI 工具（task-003）实现。
"""
