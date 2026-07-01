"""Phase 1.4 端到端 demo 使用的节点函数。

提供给 ``examples/cli_demo.yaml`` 中的 passthrough 节点引用。
"""


def increment(state: dict) -> dict:
    """将 value 加 1。"""
    return {"value": state.get("value", 0) + 1, "log": state.get("log", []) + ["inc"]}


def double(state: dict) -> dict:
    """将 value 翻倍。"""
    return {"value": state["value"] * 2, "log": state.get("log", []) + ["dbl"]}
