import { Tag, Divider, Button, Modal } from "antd";
import { ReloadOutlined, ClockCircleOutlined, ThunderboltOutlined, FileTextOutlined } from "@ant-design/icons";
import type { NodeExecution } from "../../api/runs";

const STATUS_META: Record<string, { label: string; color: string }> = {
  pending:         { label: "Pending",  color: "#FBBF24" },
  running:         { label: "Running",  color: "#3B82F6" },
  success:         { label: "Success",  color: "#10B981" },
  failed:          { label: "Failed",   color: "#EF4444" },
  skipped:         { label: "Skipped",  color: "#9CA3AF" },
  waiting_approval:{ label: "Waiting",  color: "#F59E0B" },
  canceled:        { label: "Canceled", color: "#6B7280" },
};

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
}

function JsonBlock({ data }: { data: unknown }) {
  const str = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  return (
    <pre style={{
      fontFamily: "'JetBrains Mono', monospace", fontSize: 11, lineHeight: 1.5,
      background: "#F8FAFC", borderRadius: 6, padding: 12, overflow: "auto",
      maxHeight: 200, color: "#1E293B", margin: 0, whiteSpace: "pre-wrap",
      wordBreak: "break-all",
    }}>
      {str}
    </pre>
  );
}

interface NodeExecutionDetailProps {
  execution: NodeExecution | null;
  
  onRetryFromNode?: (nodeId: string) => void;
}

export function NodeExecutionDetail({ execution, onRetryFromNode }: NodeExecutionDetailProps) {
  if (!execution) {
    return (
      <div style={{ padding: 32, textAlign: "center", color: "var(--text-muted)", fontSize: 13 }}>
        <FileTextOutlined style={{ fontSize: 24, display: "block", marginBottom: 12, opacity: 0.3 }} />
        Select a node to view execution details
      </div>
    );
  }

  const statusMeta = STATUS_META[execution.status] || { label: execution.status, color: "#6B7280" };

  const handleRetryFromClick = () => {
    if (!execution) return;
    Modal.confirm({
      title: "Retry from this node?",
      content: `This will create a new run starting from "${execution.nodeName}". The failed node and all subsequent nodes will be re-executed.`,
      okText: "Retry from here",
      okButtonProps: { danger: true, icon: <ReloadOutlined /> },
      cancelText: "Cancel",
      onOk: () => {
        if (onRetryFromNode && execution) {
          onRetryFromNode(execution.nodeId);
        }
      },
    });
  };

  return (
    <div style={{ padding: 16, fontSize: 13, overflow: "auto", height: "100%" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14, color: "var(--text-primary)" }}>{execution.nodeName}</div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", fontFamily: "'JetBrains Mono', monospace" }}>
            {execution.nodeId} - {execution.nodeType}
          </div>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 4 }}>
          <Tag color={statusMeta.color} style={{ borderRadius: 4, fontSize: 11 }}>{statusMeta.label}</Tag>
          {execution.status === "failed" && onRetryFromNode && (
            <Button
              type="text"
              size="small"
              icon={<ReloadOutlined />}
              onClick={handleRetryFromClick}
              style={{ color: "#EF4444", fontSize: 11, padding: "0 4px" }}
            >
              Retry from here
            </Button>
          )}
        </div>
      </div>

      {/* Timing */}
      <div style={{ display: "flex", gap: 16, marginBottom: 16, fontSize: 12, color: "var(--text-secondary)" }}>
        {execution.startTime && (
          <div>
            <ClockCircleOutlined style={{ marginRight: 4, fontSize: 11 }} />
            {new Date(execution.startTime).toLocaleTimeString()}
          </div>
        )}
        <div>
          <ThunderboltOutlined style={{ marginRight: 4, fontSize: 11 }} />
          {formatDuration(execution.duration)}
        </div>
        {execution.tokensUsed != null && (
          <div style={{ color: "var(--text-muted)" }}>
            {execution.tokensUsed.toLocaleString()} tokens
          </div>
        )}
      </div>

      <Divider style={{ margin: "0 0 16px 0" }} />

      {/* Error */}
      {execution.error && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: "#EF4444", marginBottom: 6 }}>Error</div>
          <pre style={{
            fontFamily: "'JetBrains Mono', monospace", fontSize: 11, lineHeight: 1.5,
            background: "#FEF2F2", borderRadius: 6, padding: 12, overflow: "auto",
            maxHeight: 120, color: "#991B1B", margin: 0, border: "1px solid #FECACA",
            whiteSpace: "pre-wrap", wordBreak: "break-all",
          }}>
            {execution.error}
          </pre>
        </div>
      )}

      {/* Input */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6, display: "flex", alignItems: "center", gap: 4 }}>
          <span>Input</span>
          {execution.input && (
            <span style={{ fontWeight: 400, color: "var(--text-muted)" }}>
              ({Object.keys(execution.input).length} fields)
            </span>
          )}
        </div>
        <JsonBlock data={execution.input} />
      </div>

      {/* Output */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 6, display: "flex", alignItems: "center", gap: 4 }}>
          <span>Output</span>
          {execution.output && (
            <span style={{ fontWeight: 400, color: "var(--text-muted)" }}>
              ({Object.keys(execution.output).length} fields)
            </span>
          )}
        </div>
        <JsonBlock data={execution.output} />
      </div>
    </div>
  );
}
