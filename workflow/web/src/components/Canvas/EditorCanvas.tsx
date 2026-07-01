import { useCallback, useRef, useEffect, useState } from "react";
import { ReactFlow, Controls, useNodesState, useEdgesState, ReactFlowProvider, type Node, type Edge, type Connection } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { CanvasNode } from "./CanvasNode";
import { CanvasGrid } from "./CanvasGrid";
import { HUD } from "../Common/HUD";
import { FlowParticles } from "./FlowParticles";
import { ConfigPanel } from "../Panels/ConfigPanel";
import { NODE_META } from "./nodeMeta";

export const nodeTypes = { canvasNode: CanvasNode };
const DEFAULT_NODES: Node[] = [
  { id: "llm_1", type: "canvasNode", position: { x: 80, y: 100 }, data: { nodeType: "llm", label: "AI 总结", description: "LLM 节点 · 智能分析", status: "running" } },
  { id: "tool_1", type: "canvasNode", position: { x: 320, y: 120 }, data: { nodeType: "tool", label: "发送通知", description: "Tool 节点 · Webhook", status: "pending" } },
  { id: "cond_1", type: "canvasNode", position: { x: 80, y: 280 }, data: { nodeType: "condition", label: "条件判断", description: "Condition 节点", status: "pending" } },
];
const DEFAULT_EDGES: Edge[] = [
  { id: "e1", source: "llm_1", target: "tool_1", animated: true, style: { stroke: "rgba(129,140,248,0.6)", strokeWidth: 2.5 } },
  { id: "e2", source: "llm_1", target: "cond_1", animated: true, style: { stroke: "rgba(52,211,153,0.5)", strokeWidth: 2 } },
];

function hasCycle(nodes: Node[], edges: Edge[]): boolean {
  const adj = new Map<string, string[]>();
  const allIds = new Set(nodes.map(n => n.id));
  edges.forEach(e => { if (!adj.has(e.source)) adj.set(e.source, []); adj.get(e.source)!.push(e.target); });
  const visited = new Set<string>(), recStack = new Set<string>();
  function dfs(id: string): boolean {
    if (recStack.has(id)) return true;
    if (visited.has(id)) return false;
    visited.add(id); recStack.add(id);
    for (const nb of (adj.get(id) || [])) { if (dfs(nb)) return true; }
    recStack.delete(id); return false;
  }
  return [...allIds].some(id => dfs(id));
}

export function EditorCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(DEFAULT_NODES);
  const [edges, setEdges, onEdgesChange] = useEdgesState(DEFAULT_EDGES);
  const [svgPaths, setSvgPaths] = useState<SVGPathElement[]>([]);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [leftOpen, setLeftOpen] = useState(false);
  const [rightOpen, setRightOpen] = useState(false);
  const [cycleError, setCycleError] = useState<string | null>(null);
  const ref = useRef<HTMLDivElement>(null);

  const onConnect = useCallback((params: Connection) => {
    const newEdge: Edge = { id: `e-${params.source}-${params.target}`, ...params, animated: true, style: { stroke: "rgba(129,140,248,0.5)", strokeWidth: 2.5 } };
    const updated = [...edges, newEdge];
    if (hasCycle(nodes, updated)) { setCycleError("循环依赖检测失败"); setTimeout(() => setCycleError(null), 3000); return; }
    setCycleError(null); setEdges(updated);
  }, [edges, nodes]);
  const onNodeClick = useCallback((_e: unknown, node: Node) => { setSelectedNode(node); setRightOpen(true); }, []);
  const onPaneClick = useCallback(() => { setSelectedNode(null); setRightOpen(false); }, []);
  useEffect(() => { const t = setTimeout(() => { if (ref.current) setSvgPaths(Array.from(ref.current.querySelectorAll<SVGPathElement>(".react-flow__edge-path"))); }, 200); return () => clearTimeout(t); }, [edges]);
  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); const type = e.dataTransfer.getData("nodeType"); if (!type || !NODE_META[type]) return;
    const rect = ref.current?.getBoundingClientRect(); if (!rect) return;
    const info = NODE_META[type];
    setNodes(nds => [...nds, { id: `n_${Date.now()}`, type: "canvasNode", position: { x: e.clientX - rect.left - 88, y: e.clientY - rect.top - 20 }, data: { nodeType: type, label: info.label, description: info.desc, status: "pending" } }]);
  }, []);
  const onDragOver = useCallback((e: React.DragEvent) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; }, []);
  useEffect(() => { const i = setInterval(() => { setNodes(nds => nds.map((n, idx) => ({ ...n, data: { ...n.data, status: idx === 0 ? (Math.random() > 0.3 ? "success" : "running") : idx === 1 ? "success" : "failed" } }))); }, 6000); return () => clearInterval(i); }, []);

  return (
    <div ref={ref} style={{ position: "relative", width: "100%", height: "100%" }}>
      <CanvasGrid />
      {cycleError && <div style={{ position: "absolute", top: 60, left: "50%", transform: "translateX(-50%)", zIndex: 50, background: "rgba(239,68,68,0.95)", color: "white", padding: "8px 20px", borderRadius: 8, fontSize: 13, boxShadow: "0 4px 20px rgba(0,0,0,0.3)" }}>{cycleError}</div>}
      <div style={{ position: "absolute", inset: 0, zIndex: 2 }}>
        <ReactFlowProvider>
          <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} onDrop={onDrop} onDragOver={onDragOver} onNodeClick={onNodeClick} onPaneClick={onPaneClick} nodeTypes={nodeTypes} fitView minZoom={0.2} maxZoom={3} defaultEdgeOptions={{ animated: true, style: { stroke: "rgba(129,140,248,0.4)", strokeWidth: 2 } }} deleteKeyCode={["Backspace", "Delete"]}>
            <Controls showInteractive={false} style={{ background: "#1E293B", border: "1px solid rgba(148,163,184,0.15)", borderRadius: 8 }} />
          </ReactFlow>
        </ReactFlowProvider>
      </div>
      <FlowParticles paths={svgPaths} />
      <HUD nodeCount={nodes.length} edgeCount={edges.length} />
      <Toggle side="left" onClick={() => setLeftOpen(o => !o)} label="≡" />
      <Toggle side="right" onClick={() => { setRightOpen(o => !o); if (rightOpen) setSelectedNode(null); }} label="⚙" />
      <LeftPanel open={leftOpen} />
      <RightPanel open={rightOpen} selectedNode={selectedNode} />
    </div>
  );
}

function Toggle({ side, onClick, label }: { side: "left" | "right"; onClick: () => void; label: string }) {
  const s: Record<string, number | string> = { position: "absolute", top: 12, zIndex: 10, width: 32, height: 32, background: "var(--shell-surface)", border: "1px solid var(--shell-border)", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: 16, color: "var(--text-secondary)", boxShadow: "0 2px 8px rgba(0,0,0,0.08)", transition: "all 200ms cubic-bezier(0.33,1,0.68,1)" };
  s[side] = 12;
  return <button onClick={onClick} style={s} onMouseEnter={e => { e.currentTarget.style.background = "var(--primary)"; e.currentTarget.style.color = "white"; }} onMouseLeave={e => { e.currentTarget.style.background = "var(--shell-surface)"; e.currentTarget.style.color = "var(--text-secondary)"; }}>{label}</button>;
}

function LeftPanel({ open }: { open: boolean }) {
  return (<div style={{ position: "absolute", top: 0, left: 0, zIndex: 30, height: "100%", background: "var(--shell-surface)", borderRight: "1px solid var(--shell-border)", boxShadow: "4px 0 24px rgba(0,0,0,0.08)", width: 220, overflowY: "auto", transform: open ? "translateX(0)" : "translateX(-100%)", transition: "transform 250ms cubic-bezier(0.33,1,0.68,1)" }}>
    <div style={{ padding: 16, borderBottom: "1px solid var(--shell-border)", fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 13 }}>节点类型</div>
    <div style={{ padding: 8 }}>{Object.entries(NODE_META).map(([type, info]) => (
      <div key={type} draggable onDragStart={e => e.dataTransfer.setData("nodeType", type)} style={{ display: "flex", alignItems: "center", gap: 10, padding: "10px 12px", borderRadius: 8, cursor: "grab", fontSize: 13, transition: "background 150ms" }}
        onMouseEnter={e => e.currentTarget.style.background = "#F1F5F9"} onMouseLeave={e => e.currentTarget.style.background = "transparent"}>
        <div style={{ width: 28, height: 28, borderRadius: 6, background: "rgba(255,255,255,0.1)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, flexShrink: 0 }}>{info.icon}</div>
        <div><div style={{ fontWeight: 500 }}>{info.label}</div><div style={{ fontSize: 11, color: "var(--text-muted)" }}>{info.desc}</div></div>
      </div>
    ))}</div></div>);
}

function RightPanel({ open, selectedNode }: { open: boolean; selectedNode: Node | null }) {
  return (<div style={{ position: "absolute", top: 0, right: 0, zIndex: 30, height: "100%", background: "var(--shell-surface)", borderLeft: "1px solid var(--shell-border)", boxShadow: "-4px 0 24px rgba(0,0,0,0.08)", width: 300, overflowY: "auto", transform: open ? "translateX(0)" : "translateX(100%)", transition: "transform 250ms cubic-bezier(0.33,1,0.68,1)" }}>
    <div style={{ padding: 16, borderBottom: "1px solid var(--shell-border)", display: "flex", justifyContent: "space-between", fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 13 }}>
      <span>节点配置</span>
      <span style={{ color: "var(--text-muted)", fontWeight: 400, fontSize: 11 }}>{selectedNode ? String(selectedNode.data.label ?? "") : "未选中"}</span>
    </div>
    {selectedNode ? <ConfigPanel nodeType={String(selectedNode.data.nodeType ?? "")} /> : <div style={{ padding: 24, textAlign: "center", color: "var(--text-muted)", fontSize: 13 }}>选择一个节点查看配置</div>}
  </div>);
}
