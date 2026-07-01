"""将 WorkflowDSL 转换为可执行的 WorkflowEngine。

支持的节点类型：
    - passthrough：通过 ``module.path:function`` 字符串引用 Python 函数。
    - llm：通过 ``params.provider``（fake/openai/anthropic，懒加载厂商包）或
      ``params.llm``（``module.path:obj`` 引用 ``BaseChatModel`` 实例/工厂）构造
      ``LLMNode``。
    - tool：通过 ``params.tool``（``module.path:obj`` 引用 ``@tool`` 装饰的
      ``BaseTool``）构造 ``ToolNode``。
    - condition：通过 ``params.condition`` 字符串表达式 + ``true_branch``/
      ``false_branch`` 构建 ``ConditionNode``。

错误信息：所有 builder 错误都包装为 ``BuilderError``，便于 CLI 友好展示。
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from typing import Any

from agent_engine.config import EngineConfig
from agent_engine.dsl.models import NodeSpec, NodeType, WorkflowDSL
from agent_engine.engine import WorkflowEngine
from agent_engine.llm import ProviderError, get_llm


class BuilderError(ValueError):
    """DSL → WorkflowEngine 构建失败的错误。"""


def build_engine(dsl: WorkflowDSL) -> WorkflowEngine:
    """根据 DSL 构建 WorkflowEngine。

    Args:
        dsl: 已通过 schema 与引用校验的 ``WorkflowDSL``。

    Returns:
        可编译执行的 ``WorkflowEngine``。

    Raises:
        BuilderError: 节点参数非法、模块导入失败、类型不支持等。
    """
    config = EngineConfig(
        recursion_limit=dsl.config.recursion_limit,
        max_concurrency=dsl.config.max_concurrency,
    )
    engine = WorkflowEngine(config=config)

    # 1. 注册所有节点
    for node in dsl.nodes:
        action = _build_node_action(node)
        engine.add_node(node.id, action)

    # 2. depends_on 自动建边（source: 被依赖者，target: 当前节点）
    for node in dsl.nodes:
        for dep in node.depends_on:
            engine.add_edge(dep, node.id)

    # 3. 显式边
    for edge in dsl.edges:
        if edge.condition is not None:
            # 条件边：根据 edge.condition 字符串路由
            # Phase 1 简化：要求 edge.source 是 condition 类型节点，
            # 并提供 evaluate(state) -> str 函数
            engine.add_conditional_edges(
                source=edge.source,
                path=lambda state, _cond=edge.condition: _cond,  # type: ignore[arg-type]
                path_map=None,
            )
        else:
            engine.add_edge(edge.source, edge.target)

    # 4. 入口 / 出口
    engine.set_entry_point(dsl.entry)
    for finish in dsl.finish:
        engine.set_finish_point(finish)

    return engine


# ------------------------------------------------------------------ #
# 节点 action 构造
# ------------------------------------------------------------------ #


def _build_node_action(node: NodeSpec) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """根据节点 type 与 params 构造可调用的 action。"""
    if node.type == "passthrough":
        return _build_passthrough_action(node)
    if node.type == "condition":
        return _build_condition_action(node)
    if node.type == "llm":
        return _build_llm_action(node)
    if node.type == "tool":
        return _build_tool_action(node)
    raise BuilderError(f"节点 {node.id!r}: 未知节点类型 {node.type!r}")


def _build_llm_action(node: NodeSpec) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """llm 节点：构造 ``LLMNode``。

    LLM 实例来源（``params.llm`` 优先）：
        1. ``params.llm`` 为 ``module.path:obj`` 字符串：
           - 若导入结果是 ``BaseChatModel`` 实例，直接使用；
           - 若是 callable，则以 ``params`` 调用（工厂模式），返回 BaseChatModel。
        2. 否则用 ``params.provider``（默认 ``"fake"``）走 ``get_llm`` 注册表。

    必填参数：``prompt_template``。可选：``output_key``（默认 ``"response"``）。
    """
    from agent_engine.nodes import LLMNode

    params = node.params
    prompt_template = params.get("prompt_template")
    if not isinstance(prompt_template, str) or not prompt_template:
        raise BuilderError(
            f"节点 {node.id!r}: llm 节点需 params.prompt_template (字符串模板), "
            f"实际值: {prompt_template!r}"
        )
    output_key = params.get("output_key", "response")

    llm = _resolve_llm(node, params)
    return LLMNode(prompt_template=prompt_template, llm=llm, output_key=output_key)


def _resolve_llm(node: NodeSpec, params: dict[str, Any]) -> Any:
    """从 params.llm（import ref）或 params.provider（注册表）解析 LLM 实例。"""
    llm_ref = params.get("llm")
    if isinstance(llm_ref, str) and llm_ref:
        obj = _import_callable(llm_ref)
        # 若是 BaseChatModel 实例直接采用；若是 callable（工厂），以 params 调用
        if hasattr(obj, "invoke") and not callable(obj):
            return obj
        if callable(obj):
            # 工厂可选两种调用约定：
            #   factory(params_dict) —— 老 API（直接示例见 examples.demo_nodes:fake_llm）
            #   factory(**kwargs)    —— LangChain 构造器风格（如 FakeListChatModel 类）
            # 先尝试 **params（过滤本注册表专用字段），失败再退化到位置参数工厂。
            ctor_kwargs = {k: v for k, v in params.items() if k not in {"llm", "provider"}}
            try:
                return obj(**ctor_kwargs)
            except TypeError:
                pass
            try:
                return obj(params)
            except ProviderError:
                raise
            except Exception as e:
                raise BuilderError(f"节点 {node.id!r}: llm 工厂 {llm_ref!r} 调用失败: {e}") from e
        raise BuilderError(
            f"节点 {node.id!r}: {llm_ref!r} 既不是 BaseChatModel 实例也不是工厂函数, "
            f"实际类型: {type(obj).__name__}"
        )

    provider = params.get("provider", "fake")
    try:
        return get_llm(provider, params)
    except ProviderError as e:
        raise BuilderError(f"节点 {node.id!r}: {e}") from e


def _build_tool_action(node: NodeSpec) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """tool 节点：通过 ``params.tool`` 的 ``module.path:obj`` 引用 ``@tool`` 装饰的对象。

    必填：``params.tool``。可选：``input_key``（默认 ``"input"``）、
    ``output_key``（默认 ``"tool_result"``）。
    """
    from agent_engine.nodes import ToolNode

    params = node.params
    tool_ref = params.get("tool")
    if not isinstance(tool_ref, str) or not tool_ref:
        raise BuilderError(
            f"节点 {node.id!r}: tool 节点需 params.tool "
            f"('module.path:tool_name' 格式), 实际值: {tool_ref!r}"
        )
    tool = _import_callable(tool_ref)
    # BaseTool 由 @tool 装饰生成，具备 invoke 方法且通常非 callable（LangChain 1.x）
    if not (hasattr(tool, "invoke") or callable(tool)):
        raise BuilderError(
            f"节点 {node.id!r}: {tool_ref!r} 解析结果不是 BaseTool 或可调用对象, "
            f"实际类型: {type(tool).__name__}"
        )

    input_key = params.get("input_key", "input")
    output_key = params.get("output_key", "tool_result")
    return ToolNode(tool=tool, input_key=input_key, output_key=output_key)


def _build_passthrough_action(node: NodeSpec) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """passthrough 节点：从 params.callable 加载 Python 函数。"""
    ref = node.params.get("callable")
    if not isinstance(ref, str) or not ref:
        raise BuilderError(
            f"节点 {node.id!r}: passthrough 节点需 params.callable "
            f"('module.path:function_name' 格式), 实际值: {ref!r}"
        )
    func = _import_callable(ref)
    if not callable(func):
        raise BuilderError(
            f"节点 {node.id!r}: {ref!r} 解析结果不是可调用对象, 实际类型: {type(func).__name__}"
        )

    # 包装：把 state 传给函数，把返回 dict 合并回 state
    def action(state: dict[str, Any]) -> dict[str, Any]:
        result = func(state)
        if result is None:
            return state
        if not isinstance(result, dict):
            raise BuilderError(
                f"节点 {node.id!r}: 函数返回值必须是 dict 或 None, "
                f"实际类型: {type(result).__name__}"
            )
        return {**state, **result}

    action.__name__ = f"passthrough_{node.id}"
    return action


def _build_condition_action(node: NodeSpec) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """condition 节点：根据 params.condition 表达式路由。

    通过 ``ConditionNode`` 实现，自动注册到 add_conditional_edges。
    返回的 action 仅作占位（passthrough 行为），不修改 state。
    """
    from agent_engine.nodes import ConditionNode

    expr = node.params.get("condition")
    if not isinstance(expr, str) or not expr:
        raise BuilderError(
            f"节点 {node.id!r}: condition 节点需 params.condition (Python 表达式), 实际值: {expr!r}"
        )
    true_branch = node.params.get("true_branch", "true")
    false_branch = node.params.get("false_branch", "false")

    # 表达式以 "lambda state: " 开头；或裸表达式（隐式 state 上下文）
    if expr.startswith("lambda "):
        cond_func = eval(expr, {"__builtins__": {}})  # noqa: S307
    else:
        # 简单 bool 表达式：编译为 lambda state: <expr>
        code = f"lambda state: bool({expr})"
        cond_func = eval(code, {"__builtins__": {}})  # noqa: S307

    cond_node = ConditionNode(
        condition=cond_func,
        true_branch=str(true_branch),
        false_branch=str(false_branch),
    )
    # 占位 action：condition 节点在 add_conditional_edges 中作为 path_func，
    # 此处返回的 lambda 永远不被实际调用（因为 edge 会用 cond_node.evaluate）。
    return cond_node


def _import_callable(ref: str) -> Any:
    """根据 'module.path:function_name' 字符串导入 Python 可调用对象。"""
    if ":" not in ref:
        raise BuilderError(f"无法解析 callable 引用 {ref!r}: 格式应为 'module.path:function_name'")
    module_path, attr = ref.split(":", 1)
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        raise BuilderError(f"无法导入模块 {module_path!r}: {e}") from e
    try:
        # 支持嵌套属性（如 obj.sub.func）
        obj: Any = module
        for part in attr.split("."):
            obj = getattr(obj, part)
    except AttributeError as e:
        raise BuilderError(f"模块 {module_path!r} 中找不到属性 {attr!r}: {e}") from e
    return obj


__all__ = ["BuilderError", "NodeType", "build_engine"]
