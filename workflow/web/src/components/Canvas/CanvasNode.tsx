import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { NODE_TYPE_META, type NodeType } from "../../types/workflow";

function CanvasNodeComponent({ data, selected }: NodeProps) {
  const nodeType = data.nodeType as NodeType;
  const meta = NODE_TYPE_META[nodeType];
  const label = data.label as string;
  const description = data.description as string;
  const status = data.status as string | undefined;
  const isRunning = status === "running";

  return (
    <div
      style={{
        width: 176, background: "#1E293B",
        border: `1.5px solid var(--node-${nodeType}, #818CF8)`,
        borderRadius: 12, padding: "14px 16px", position: "relative",
        cursor: "grab", transition: "all 300ms cubic-bezier(0.33,1,0.68,1)",
        boxShadow: selected
          ? "0 0 0 2px var(--primary), 0 0 20px rgba(129,140,248,0.3)"
          : isRunning
          ? "0 0 6px var(--node-llm), 0 0 12px rgba(255,255,255,0.04)"
          : undefined,
        animation: isRunning ? "node-breath 2.5s ease-in-out infinite" : undefined,
      }}
    >
      {status && status !== "pending" && (
        <div
          style={{
            position: "absolute", top: -4, right: -4, width: 12, height: 12,
            borderRadius: "50%", border: "2px solid #1E293B",
            background: status === "success" ? "var(--success)" : status === "failed" ? "var(--error)" : "var(--status-running)",
            boxShadow: status === "running" ? "0 0 8px var(--status-running)" : undefined,
            animation: status === "running" ? "badge-pulse 1s ease-in-out infinite" : undefined,
          }}
        />
      )}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <div style={{ width: 24, height: 24, borderRadius: 6, background: "rgba(255,255,255,0.08)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13 }}>
          {meta?.icon || "⚡"}
        </div>
        <div style={{ fontFamily: "var(--font-display)", fontSize: 13, fontWeight: 600, color: "#F1F5F9" }}>{label}</div>
      </div>
      {description && <div style={{ fontSize: 11, color: "#64748B", lineHeight: 1.4 }}>{description}</div>}
      <Handle type="target" position={Position.Top} style={{ width: 10, height: 10, background: "var(--canvas-bg)", border: "2px solid var(--node-llm)", top: -5 }} />
      <Handle type="source" position={Position.Bottom} style={{ width: 10, height: 10, background: "var(--canvas-bg)", border: "2px solid var(--node-llm)", bottom: -5 }} />
    </div>
  );
}
export const CanvasNode = memo(CanvasNodeComponent);
