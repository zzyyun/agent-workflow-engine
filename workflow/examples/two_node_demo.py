"""2 节点最小工作流 demo。

流程：
    START -> increment -> double -> END

节点：
    - increment: 将输入中的 ``value`` +1
    - double:   将 ``value`` 翻倍

运行：
    python examples/two_node_demo.py
"""

from __future__ import annotations

import logging
import os
import sys

# 允许直接 ``python examples/two_node_demo.py`` 运行
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent_engine import EngineConfig, WorkflowEngine  # noqa: E402


def increment(state: dict) -> dict:
    """节点 1：将 value 加 1。"""
    new_state = dict(state)  # 复制原 state
    new_state["value"] = state.get("value", 0) + 1
    return new_state


def double(state: dict) -> dict:
    """节点 2：将 value 翻倍。"""
    new_state = dict(state)
    new_state["value"] = state["value"] * 2
    return new_state


def build_engine() -> WorkflowEngine:
    """构建 2 节点工作流引擎。"""
    engine = WorkflowEngine(EngineConfig(recursion_limit=25))
    engine.add_node("increment", increment)
    engine.add_node("double", double)
    engine.add_edge("increment", "double")
    engine.set_entry_point("increment")
    engine.set_finish_point("double")
    return engine


def main() -> None:
    """运行 demo 并打印结果。"""
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )

    engine = build_engine()
    compiled = engine.compile()

    # invoke 模式：返回最终 state
    print("=" * 50)
    print("[invoke] 初始 state: {'value': 3}")
    final = compiled.invoke({"value": 3})
    print(f"[invoke] 最终 state: {final}")
    # 期望: 3 -> increment=4 -> double=8
    assert final["value"] == 8, f"期望 value=8, 实际 value={final['value']}"

    # stream 模式：逐步产出节点输出
    print("=" * 50)
    print("[stream] 初始 state: {'value': 1}")
    chunks = list(compiled.stream({"value": 1}))
    for chunk in chunks:
        print(f"[stream] 节点输出: {chunk}")
    # 期望: 1 -> increment=2 -> double=4
    last_value = chunks[-1]["double"]["value"]
    assert last_value == 4, f"期望最终 value=4, 实际 value={last_value}"

    print("=" * 50)
    print("✅ Demo 运行成功")


if __name__ == "__main__":
    main()
