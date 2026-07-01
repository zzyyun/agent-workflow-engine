"""LangChain 节点适配层。

Phase 1.2 交付物：基于 LangChain Runnable 协议的统一节点抽象，
内置 LLM / Tool / Condition 三种节点类型。

所有节点实现统一的 ``invoke(state) -> state`` 接口，
可被 ``WorkflowEngine.add_node()`` 直接使用，也可转为
LangChain ``Runnable`` 嵌入 LangGraph。
"""

from agent_engine.nodes.base import NodeAdapter
from agent_engine.nodes.condition_node import ConditionNode
from agent_engine.nodes.llm_node import LLMNode
from agent_engine.nodes.tool_node import ToolNode

__all__ = [
    "ConditionNode",
    "LLMNode",
    "NodeAdapter",
    "ToolNode",
]
