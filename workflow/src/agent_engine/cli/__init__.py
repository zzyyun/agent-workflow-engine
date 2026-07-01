"""Agent Workflow Engine CLI。

提供三个子命令：
    - ``agent-engine validate <dsl>``  校验 DSL 文件
    - ``agent-engine run <dsl>``        执行 DSL 工作流
    - ``agent-engine resume <run_id>``  续跑（Phase 1 占位，Phase 2 接入 PostgresSaver）

使用 ``python -m agent_engine.cli <command>`` 入口。
"""
