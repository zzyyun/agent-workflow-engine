import { useCallback, useRef, useEffect, useState } from "react";
import { ReactFlow, Controls, addEdge, useNodesState, useEdgesState, ReactFlowProvider, type Node, type Edge, type Connection } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { CanvasNode } from "./CanvasNode";
import { CanvasGrid } from "./CanvasGrid";
import { HUD } from "../Common/HUD";
import { EmptyCanvas } from "../Common/EmptyCanvas";
import { FlowParticles } from "./FlowParticles";

const nodeTypes = { canvasNode: CanvasNode };
const DEFAULT_NODES: Node[] = [
  { id: "llm_1", type: "canvasNode", position: { x: 80, y: 100 }, data: { nodeType: "llm", label: "AI 总结", description: "LLM 节点 · 智能分析", status: "running" } },
  { id: "tool_1", type: "canvasNode", position: { x: 320, y: 120 }, data: { nodeType: "tool", label: "发送通知", description: "Tool 节点 · Webhook", status: "pending" } },
  { id: "cond_1", type: "canvasNode", position: { x: 80, y: 280 }, data: { nodeType: "condition", label: "条件判断", description: "Condition 节点", status: "pending" } },
];
const DEFAULT_EDGES: Edge[] = [
  { id: "e1", source: "llm_1", target: "tool_1", animated: true, style: { stroke: "rgba(129,140,248,0.6)", strokeWidth: 2.5 } },
  { id: "e2", source: "llm_1", target: "cond_1", animated: true, style: { stroke: "rgba(52,211,153,0.5)", strokeWidth: 2 } },
];
const NODE_META: Record<string, { label: string; desc: string }> = {
  llm: { label: "LLM 节点", desc: "LLM 节点" }, tool: { label: "工具调用", desc: "Tool 节点" }, condition: { label: "条件判断", desc: "Condition 节点" },
  loop: { label: "循环", desc: "Loop 节点" }, retriever: { label: "知识检索", desc: "Retriever 节点" }, approval: { label: "审批", desc: "Approval 节点" },
  http: { label: "HTTP 请求", desc: "HTTP 节点" }, subworkflow: { label: "子流程", desc: "SubFlow 节点" },
};

export function EditorCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(DEFAULT_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState(DEFAULT_EDGES);
  const [svgPaths, setSvgPaths] = useState<SVGPathElement[]>([]);
  const [showEmpty] = useState(false);
  const reactFlowRef = useRef<HTMLDivElement>(null);

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge({ ...params, animated: true, style: { stroke: "rgba(129,140,248,0.5)", strokeWidth: 2.5 } }, eds)), []);
  useEffect(() => {
    const timer = setTimeout(() => { if (reactFlowRef.current) { setSvgPaths(Array.from(reactFlowRef.current.querySelectorAll<SVGPathElement>(".react-flow__edge-path"))); } }, 200);
    return () => clearTimeout(timer);
  }, [edges]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const type = e.dataTransfer.getData("nodeType");
    if (!type || !NODE_META[type]) return;
    const rect = reactFlowRef.current?.getBoundingClientRect();
    if (!rect) return;
    const info = NODE_META[type];
    setNodes((nds) => [...nds, { id: `node_${Date.now()}`, type: "canvasNode", position: { x: e.clientX - rect.left - 88, y: e.clientY - rect.top - 20 }, data: { nodeType: type, label: info.label, description: info.desc, status: "pending" } }]);
  }, []);
  const onDragOver = useCallback((e: React.DragEvent) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; }, []);
  useEffect(() => { const i = setInterval(() => { setNodes((nds) => nds.map((n, idx) => ({ ...n, data: { ...n.data, status: idx === 0 ? (Math.random() > 0.3 ? "success" : "running") : idx === 1 ? "success" : "failed" } }))); }, 6000); return () => clearInterval(i); }, []);

  return (
    <div ref={reactFlowRef} style={{ position: "relative", width: "100%", height: "100%" }}>
      <CanvasGrid />
      <div style={{ position: "absolute", inset: 0, zIndex: 2 }}>
        <ReactFlowProvider>
          <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} onDrop={onDrop} onDragOver={onDragOver} nodeTypes={nodeTypes} fitView minZoom={0.2} maxZoom={3}
            defaultEdgeOptions={{ animated: true, style: { stroke: "rgba(129,140,248,0.4)", strokeWidth: 2 } }}
          >
            <Controls showInteractive={false} style={{ background: "#1E293B", border: "1px solid rgba(148,163,184,0.15)", borderRadius: 8 }} />
          </ReactFlow>
        </ReactFlowProvider>
      </div>
      <FlowParticles paths={svgPaths} />
      <HUD />
      <EmptyCanvas visible={showEmpty} />
    </div>
  );
}
