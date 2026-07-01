"""WorkflowEngine 核心实现：封装 LangGraph StateGraph。

设计目标：
    1. 屏蔽 LangGraph 的实现细节，对外提供稳定的 Pythonic API。
    2. 统一管理节点、边、条件边，并做引用完整性校验。
    3. 通过 ``EngineConfig`` 暴露 ``recursion_limit`` 与 ``max_concurrency``。
    4. ``invoke()`` / ``stream()`` 会在首次执行时按需自动调用 ``compile()``；
       也可手动提前 ``compile()`` 以提前暴露图结构错误（如未设置入口节点）。
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Hashable, Mapping, Sequence
from typing import Annotated, Any, TypeAlias

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from agent_engine.config import (
    EdgeError,
    EngineConfig,
    NodeAlreadyExistsError,
    NodeNotFoundError,
)

logger = logging.getLogger(__name__)

# 节点处理函数签名：接收 state，返回更新后的 state（dict）
NodeAction: TypeAlias = Callable[[dict[str, Any]], dict[str, Any] | Any]
# 条件边路径函数：接收 state，返回目标节点名（或 [END]）
PathFunction: TypeAlias = Callable[[dict[str, Any]], str | Sequence[str]]
# 条件边路径映射：路径 -> 目标节点名
PathMap: TypeAlias = Mapping[Hashable, str]


def _merge_dicts(left: dict[str, Any] | None, right: dict[str, Any] | None) -> dict[str, Any]:
    """并行节点返回的 dict 合并 reducer。"""
    return {**(left or {}), **(right or {})}


class _EngineState(TypedDict, total=False):
    """WorkflowEngine 内部使用的 state schema。

    使用 ``__root__`` channel + 合并 reducer，使得多个并行节点返回的
    字典能够被自动合并（否则会抛 ``InvalidUpdateError``）。
    """

    __root__: Annotated[dict[str, Any], _merge_dicts]


class WorkflowEngine:
    """工作流执行引擎（基于 LangGraph StateGraph）。

    使用示例::

        engine = WorkflowEngine()
        engine.add_node("a", lambda s: {"value": s.get("value", 0) + 1})
        engine.add_node("b", lambda s: {"value": s["value"] * 2})
        engine.add_edge("a", "b")
        engine.set_entry_point("a")
        engine.set_finish_point("b")
        compiled = engine.compile()
        result = compiled.invoke({"value": 1})
    """

    def __init__(self, config: EngineConfig | None = None) -> None:
        """初始化引擎。

        Args:
            config: 引擎配置；为 None 时使用默认配置（recursion_limit=25）。
        """
        self._config = config or EngineConfig()
        # 保存用户注册的节点与边，便于校验与状态查询
        self._nodes: dict[str, NodeAction] = {}
        # 普通边：start -> end
        self._edges: list[tuple[str, str]] = []
        # 条件边：(source, path_func, path_map) — path_map 可为 None
        self._conditional_edges: list[tuple[str, PathFunction, PathMap | None]] = []
        # 入口 / 出口节点
        self._entry_point: str | None = None
        self._finish_points: list[str] = []
        # 编译后缓存
        self._compiled = None
        # 动态生成的 state TypedDict schema（带 reducer），首次编译时创建
        self._state_schema = None
        # LangGraph checkpointer（持久化/续跑用），None 表示无持久化
        self._checkpointer = None

    # ------------------------------------------------------------------ #
    # 属性
    # ------------------------------------------------------------------ #

    @property
    def config(self) -> EngineConfig:
        """当前引擎配置。"""
        return self._config

    @property
    def node_names(self) -> list[str]:
        """已注册的节点名称列表。"""
        return list(self._nodes.keys())

    def has_node(self, name: str) -> bool:
        """判断指定节点是否已注册。"""
        return name in self._nodes

    def with_checkpointer(self, checkpointer):
        """为引擎挂载 LangGraph checkpointer，启用断点持久化与续跑。

        Args:
            checkpointer: ``langgraph.checkpoint.*`` 的 saver 实例（如
                ``MemorySaver`` / ``PostgresSaver``），或 ``None`` 取消挂载。

        Returns:
            self，便于链式调用。

        Note:
            挂载会失效已编译的图缓存，下次执行时按新 checkpointer 重新编译。
            真正的 thread 标识通过 ``invoke(stream)`` 的 ``config['configurable']['thread_id']``
            传入，本方法只负责把 saver 接入图。
        """
        self._checkpointer = checkpointer
        # 使旧编译产物失效
        self._compiled = None
        logger.debug("挂载 checkpointer: %s", type(checkpointer).__name__ if checkpointer else None)
        return self

    # ------------------------------------------------------------------ #
    # 节点注册
    # ------------------------------------------------------------------ #

    def add_node(self, name: str, action: NodeAction) -> WorkflowEngine:
        """注册一个执行节点。

        Args:
            name: 节点名称，在当前引擎内必须唯一。
            action: 节点处理函数。接受两种形式：
                1. 可调用对象 ``Callable[[dict], dict]``（普通函数 / NodeAdapter 子类）。
                2. LangChain ``Runnable``（通过 duck typing 检查 ``invoke`` 方法，
                   LangChain 1.x 的 ``RunnableLambda`` 不再是 callable，必须这样传入）。

        Returns:
            self，便于链式调用。

        Raises:
            NodeAlreadyExistsError: 节点名称已被占用。
            ValueError: 名称非法或 action 既不可调用也无 invoke 方法。
        """
        if not name or not isinstance(name, str):
            raise ValueError(f"节点名称必须为非空字符串，实际值: {name!r}")
        # 兼容 LangChain Runnable：callable 或有 invoke 方法即可
        is_runnable = hasattr(action, "invoke") and callable(getattr(action, "invoke", None))
        if not (callable(action) or is_runnable):
            raise ValueError(
                f"节点 action 必须是可调用对象或 LangChain Runnable, "
                f"实际类型: {type(action).__name__}"
            )
        if name in self._nodes:
            raise NodeAlreadyExistsError(f"节点 {name!r} 已存在，无法重复注册")
        # START / END 是 LangGraph 保留字，禁止作为节点名
        if name in (START, END):
            raise ValueError(f"节点名称 {name!r} 为 LangGraph 保留字，禁止使用")

        self._nodes[name] = action
        logger.debug("注册节点: %s", name)
        return self

    # ------------------------------------------------------------------ #
    # 边注册
    # ------------------------------------------------------------------ #

    def add_edge(self, source: str, target: str) -> WorkflowEngine:
        """添加一条固定边（source -> target）。

        Args:
            source: 起始节点名；可传 ``START`` 表示入口（与 ``set_entry_point()`` 等价）。
            target: 目标节点名；可传 ``END`` 表示结束。

        Returns:
            self，便于链式调用。

        Raises:
            EdgeError: 入口已通过不同值设置（与 ``set_entry_point()`` 或先前的 ``START`` 边冲突）。
            NodeNotFoundError: source/target 节点未注册。
            ValueError: source/target 不是合法字符串。
        """
        self._validate_edge_endpoint(source)
        self._validate_edge_endpoint(target)
        # ``add_edge(START, X)`` 与 ``set_entry_point(X)`` 等价，统一记入 _entry_point
        if source == START:
            if self._entry_point is not None and self._entry_point != target:
                raise EdgeError(
                    f"入口已设置为 {self._entry_point!r}，不能再添加 add_edge(START, {target!r})"
                )
            self._entry_point = target
        elif source not in self._nodes:
            # 边允许从 START 出发，否则要求源节点已注册
            raise NodeNotFoundError(f"源节点 {source!r} 未注册")
        # 边允许到 END，否则要求目标节点已注册
        if target != END and target not in self._nodes:
            raise NodeNotFoundError(f"目标节点 {target!r} 未注册")

        self._edges.append((source, target))
        logger.debug("添加边: %s -> %s", source, target)
        return self

    def add_conditional_edges(
        self,
        source: str,
        path: PathFunction,
        path_map: PathMap | None = None,
    ) -> WorkflowEngine:
        """添加条件边：根据 ``path`` 的返回值决定下一个节点。

        Args:
            source: 起始节点名（必须已注册）。
            path: 路径函数，接收 state，返回目标节点名（字符串或字符串列表）。
            path_map: 路径值到目标节点名的映射；为 None 时直接使用 ``path`` 的返回值。

        Returns:
            self，便于链式调用。
        """
        if source != START and source not in self._nodes:
            raise NodeNotFoundError(f"源节点 {source!r} 未注册")
        if not callable(path):
            raise ValueError("条件边的 path 函数必须是可调用对象")
        # 校验 path_map 的目标节点都已注册（END 除外）
        if path_map:
            for key, dest in path_map.items():
                if dest != END and dest not in self._nodes:
                    raise NodeNotFoundError(f"path_map 中目标节点 {dest!r} (key={key!r}) 未注册")

        self._conditional_edges.append((source, path, path_map))
        logger.debug("添加条件边: source=%s, path_map=%s", source, bool(path_map))
        return self

    # ------------------------------------------------------------------ #
    # 入口 / 出口
    # ------------------------------------------------------------------ #

    def set_entry_point(self, name: str) -> WorkflowEngine:
        """设置工作流的入口节点。

        与 ``add_edge(START, name)`` 等价——两种写法可以任选其一，
        重复设置同一入口不会报错，但设置为不同入口会抛 ``EdgeError``。

        Args:
            name: 入口节点名（必须已注册）。

        Raises:
            NodeNotFoundError: 入口节点未注册。
            EdgeError: 入口已通过其他值设置（与先前的 ``set_entry_point()`` 或 ``add_edge(START, ...)`` 冲突）。
        """
        if name not in self._nodes:
            raise NodeNotFoundError(f"入口节点 {name!r} 未注册")
        # 入口表达方式统一为 ``_entry_point``，避免 add_edge(START, X) 与 set_entry_point 出现歧义
        if self._entry_point is not None and self._entry_point != name:
            raise EdgeError(
                f"入口已设置为 {self._entry_point!r}，不能再调用 set_entry_point({name!r})"
            )
        self._entry_point = name
        logger.debug("设置入口: %s", name)
        return self

    def set_finish_point(self, name: str) -> WorkflowEngine:
        """设置工作流的结束节点。

        Args:
            name: 结束节点名（必须已注册）。
        """
        if name not in self._nodes:
            raise NodeNotFoundError(f"结束节点 {name!r} 未注册")
        if name not in self._finish_points:
            self._finish_points.append(name)
        logger.debug("设置结束: %s", name)
        return self

    # ------------------------------------------------------------------ #
    # 编译 & 执行
    # ------------------------------------------------------------------ #

    def compile(self):
        """编译当前图为可执行的 ``CompiledGraph``。

        Raises:
            EdgeError: 入口节点未设置或图结构不合法。
        """
        if self._entry_point is None:
            raise EdgeError("尚未调用 set_entry_point() 或 add_edge(START, ...) 设置入口节点")
        if not self._nodes:
            raise EdgeError("图中没有节点，无法编译")
        # 若无显式 finish_point 但有条件边到 END，仍可编译

        # 使用模块级 _EngineState（带 reducer 的 TypedDict）作为 state schema，
        # 让并行节点返回的 dict 能被自动合并。
        graph = StateGraph(_EngineState)
        # 注册所有节点
        for name, action in self._nodes.items():
            graph.add_node(name, action)
        # 注册入口
        graph.add_edge(START, self._entry_point)
        # 注册普通边
        for src, dst in self._edges:
            if src == START:
                # 入口边已通过上面的 graph.add_edge(START, self._entry_point) 表达，
                # 跳过避免 LangGraph 报重复边。
                continue
            graph.add_edge(src, dst)
        # 注册条件边
        for src, path, path_map in self._conditional_edges:
            if path_map is not None:
                graph.add_conditional_edges(src, path, path_map)
            else:
                graph.add_conditional_edges(src, path)
        # 注册结束节点
        for finish in self._finish_points:
            graph.add_edge(finish, END)

        # 新版 LangGraph 不再在 compile() 上接受 recursion_limit，
        # 改为在 invoke/stream 时通过 config 传入（见 _make_config）。
        # checkpointer 为 None 时退化为无持久化编译，保持向后兼容。
        self._compiled = graph.compile(checkpointer=self._checkpointer)
        logger.info(
            "WorkflowEngine 编译完成: 节点=%d, 边=%d, 条件边=%d, recursion_limit=%d",
            len(self._nodes),
            len(self._edges),
            len(self._conditional_edges),
            self._config.recursion_limit,
        )
        return self._compiled

    def invoke(
        self,
        state: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """同步执行工作流，返回最终 state。

        Args:
            state: 初始 state 字典。
            config: 透传给 ``CompiledGraph.invoke()`` 的 RunnableConfig；会与引擎
                默认的 ``recursion_limit`` 合并，调用方显式指定优先。
            **kwargs: 透传给 ``CompiledGraph.invoke()`` 的额外参数。

        Returns:
            最终的 state 字典。
        """
        compiled = self._ensure_compiled()
        merged_config = self._build_config(config)
        return compiled.invoke(state or {}, config=merged_config, **kwargs)

    async def ainvoke(
        self,
        state: dict[str, Any] | None = None,
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """异步执行工作流，返回最终 state。"""
        compiled = self._ensure_compiled()
        merged_config = self._build_config(config)
        return await compiled.ainvoke(state or {}, config=merged_config, **kwargs)

    def stream(
        self,
        state: dict[str, Any] | None = None,
        stream_mode: str = "updates",
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        """流式执行工作流，逐步产出节点输出。

        Args:
            state: 初始 state 字典。
            stream_mode: 流式模式（``updates`` / ``values`` / ``events``），默认 ``updates``。
            config: 透传给 ``CompiledGraph.stream()`` 的 RunnableConfig；会与引擎
                默认的 ``recursion_limit`` 合并，调用方显式指定优先。
            **kwargs: 透传给 ``CompiledGraph.stream()`` 的额外参数。

        Yields:
            每个节点执行后的输出片段。
        """
        compiled = self._ensure_compiled()
        merged_config = self._build_config(config)
        yield from compiled.stream(
            state or {}, stream_mode=stream_mode, config=merged_config, **kwargs
        )

    async def astream(
        self,
        state: dict[str, Any] | None = None,
        stream_mode: str = "updates",
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        """异步流式执行工作流。"""
        compiled = self._ensure_compiled()
        merged_config = self._build_config(config)
        async for chunk in compiled.astream(
            state or {}, stream_mode=stream_mode, config=merged_config, **kwargs
        ):
            yield chunk

    # ------------------------------------------------------------------ #
    # 内部辅助
    # ------------------------------------------------------------------ #

    def _ensure_compiled(self):
        """确保图已编译，否则触发编译。"""
        if self._compiled is None:
            return self.compile()
        return self._compiled

    def _build_config(self, user_config: dict[str, Any] | None) -> dict[str, Any]:
        """合并用户 config 与引擎默认的 ``recursion_limit``。

        调用方传入的 ``config["recursion_limit"]`` 优先级高于引擎默认值，
        便于在单次调用中临时调整递归上限。
        """
        base: dict[str, Any] = {
            "recursion_limit": self._config.recursion_limit,
        }
        if user_config:
            # 用户配置覆盖默认
            base.update(user_config)
        return base

    @staticmethod
    def _validate_edge_endpoint(name: str) -> None:
        """校验边端点名称合法性。"""
        if not name or not isinstance(name, str):
            raise ValueError(f"边端点名称必须为非空字符串, 实际值: {name!r}")


__all__ = ["PathFunction", "PathMap", "NodeAction", "WorkflowEngine"]
