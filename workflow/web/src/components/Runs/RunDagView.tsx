import { useRef, useEffect, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ReactFlowProvider,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import type { NodeExecution } from "../../api/runs";

interface RunDagViewProps {
  nodes: NodeExecution[];
  selectedNodeId: string | null;
  onNodeSelect: (nodeId: string | null) => void;
}

function getStatusColor(status: string): string {
  const m: Record<string, string> = {
    pending: "#FBBF24",
    running: "#3B82F6",
    success: "#10B981",
    failed: "#EF4444",
    skipped: "#9CA3AF",
    waiting_approval: "#F59E0B",
    canceled: "#6B7280",
  };
  return m[status] || "#9CA3AF";
}

function getStatusBg(status: string): string {
  return `${getStatusColor(status)}15`;
}

function autoLayout(executions: NodeExecution[]): { nodes: Node[]; edges: Edge[] } {
  const NODE_W = 160;
  const NODE_H = 60;
  const H_GAP = 40;
  const V_GAP = 80;
  const COLS = 3;

  const flowNodes: Node[] = executions.map((ex, idx) => {
    const col = idx % COLS;
    const row = Math.floor(idx / COLS);
    return {
      id: ex.nodeId,
      type: "default",
      position: {
        x: col * (NODE_W + H_GAP) + 20,
        y: row * (NODE_H + V_GAP) + 20,
      },
      data: {
        label: ex.nodeName,
        status: ex.status,
        nodeType: ex.nodeType,
        duration: ex.duration,
      },
      style: {
        width: NODE_W,
        padding: "8px 12px",
        borderRadius: 8,
        border: "1.5px solid",
        borderColor: getStatusColor(ex.status),
        background: getStatusBg(ex.status),
        fontFamily: "Inter, system-ui",
        fontSize: 12,
        color: "#1E293B",
        boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
      },
    };
  });

  const flowEdges: Edge[] = [];
  for (let i = 0; i < executions.length - 1; i++) {
    flowEdges.push({
      id: `e-${executions[i].nodeId}-${executions[i + 1].nodeId}`,
      source: executions[i].nodeId,
      target: executions[i + 1].nodeId,
      animated: executions[i + 1].status === "running",
      style: {
        stroke: getStatusColor(executions[i + 1].status),
        strokeWidth: 2,
        opacity: 0.6,
      },
    });
  }

  return { nodes: flowNodes, edges: flowEdges };
}

export function RunDagView({ nodes, selectedNodeId, onNodeSelect }: RunDagViewProps) {
  const { nodes: layoutNodes, edges: layoutEdges } = useMemo(() => autoLayout(nodes), [nodes]);
  const [flowNodes, setFlowNodes, onNodesChange] = useNodesState(layoutNodes);
  const [flowEdges, setFlowEdges, onEdgesChange] = useEdgesState(layoutEdges);
  const hasInit = useRef(false);

  useEffect(() => {
    if (!hasInit.current || flowNodes.length !== layoutNodes.length) {
      setFlowNodes(layoutNodes);
      setFlowEdges(layoutEdges);
      hasInit.current = true;
    }
  }, [layoutNodes, layoutEdges, setFlowNodes, setFlowEdges, flowNodes.length]);

  return (
    <ReactFlowProvider>
      <div style={{ width: "100%", height: "100%", position: "relative" }}>
        <ReactFlow
          nodes={flowNodes.map(n => ({
            ...n,
            selected: n.id === selectedNodeId,
            style: {
              ...n.style,
              borderColor: n.id === selectedNodeId
                ? getStatusColor((n.data as Record<string, unknown>).status as string)
                : getStatusColor((n.data as Record<string, unknown>).status as string),
              boxShadow: n.id === selectedNodeId
                ? `0 0 0 2px ${getStatusColor((n.data as Record<string, unknown>).status as string)}40`
                : "0 2px 8px rgba(0,0,0,0.06)",
            },
          }))}
          edges={flowEdges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={(_e, node) => onNodeSelect(node.id)}
          onPaneClick={() => onNodeSelect(null)}
          fitView
          minZoom={0.3}
          maxZoom={2}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#E2E8F0" gap={20} size={1} />
          <Controls showInteractive={false} style={{ background: "white", border: "1px solid #E2E8F0", borderRadius: 8 }} />
          <MiniMap
            nodeColor={(n) => getStatusBg((n.data as Record<string, unknown>)?.status as string || "pending")}
            style={{ background: "white", border: "1px solid #E2E8F0", borderRadius: 8 }}
            maskColor="rgba(0,0,0,0.05)"
          />
        </ReactFlow>

        {/* Legend */}
        <div style={{
          position: "absolute", bottom: 16, left: 16, zIndex: 10,
          background: "white", borderRadius: 8, padding: "8px 12px",
          border: "1px solid #E2E8F0", fontSize: 11,
          display: "flex", gap: 10, flexWrap: "wrap",
          boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
        }}>
          {[
            { status: "pending", label: "Pending" },
            { status: "running", label: "Running" },
            { status: "success", label: "Success" },
            { status: "failed", label: "Failed" },
            { status: "skipped", label: "Skipped" },
            { status: "canceled", label: "Canceled" },
          ].map(({ status, label }) => (
            <div key={status} style={{ display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{
                width: 8, height: 8, borderRadius: "50%",
                background: getStatusColor(status),
              }} />
              <span style={{ color: "#64748B" }}>{label}</span>
            </div>
          ))}
        </div>

        {/* Node count badge */}
        <div style={{
          position: "absolute", top: 16, right: 16, zIndex: 10,
          background: "white", borderRadius: 8, padding: "4px 10px",
          border: "1px solid #E2E8F0", fontSize: 11, color: "#64748B",
          boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
        }}>
          {nodes.length} nodes
        </div>
      </div>
    </ReactFlowProvider>
  );
}
