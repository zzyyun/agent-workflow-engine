import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
 import { Button, Tag, message, Spin, Alert, Tooltip, Segmented } from "antd";
 import { Modal } from "antd";
 import {
  ArrowLeftOutlined,
  ReloadOutlined,
  StopOutlined,
  ClockCircleOutlined,
  ApartmentOutlined,
  UnorderedListOutlined,
  RightOutlined,
} from "@ant-design/icons";
 import { getRun, retryRun, cancelRun, type RunDetail, type NodeExecution } from "../api/runs";
 import { retryFromNode } from "../api/runs";
import { RunDagView } from "../components/Runs/RunDagView";
import { NodeExecutionDetail } from "../components/Runs/NodeExecutionDetail";

const RUN_STATUS_META: Record<string, { label: string; color: string }> = {
  pending:         { label: "Pending",  color: "#FBBF24" },
  running:         { label: "Running",  color: "#3B82F6" },
  success:         { label: "Success",  color: "#10B981" },
  failed:          { label: "Failed",   color: "#EF4444" },
  waiting_approval:{ label: "Waiting",  color: "#F59E0B" },
  canceled:        { label: "Canceled", color: "#6B7280" },
};

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  const m = Math.floor(ms / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  return `${m}m ${s}s`;
}

function TimelineView({ executions }: { executions: NodeExecution[] }) {
  const sorted = [...executions].sort((a, b) => new Date(a.startTime).getTime() - new Date(b.startTime).getTime());
  const totalDuration = sorted.reduce((sum, ex) => sum + ex.duration, 0) || 1;

  return (
    <div style={{ padding: 16, height: "100%", overflow: "auto" }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-secondary)", marginBottom: 16 }}>
        Execution Timeline ({sorted.length} steps)
      </div>
      {sorted.map((ex, idx) => {
        const pct = Math.max((ex.duration / totalDuration) * 100, 2);
        const statusColor = RUN_STATUS_META[ex.status]?.color || "#9CA3AF";
        return (
          <div key={ex.nodeId} style={{ marginBottom: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
              <div style={{
                width: 20, height: 20, borderRadius: "50%",
                background: `${statusColor}20`,
                border: `2px solid ${statusColor}`,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 10, fontWeight: 600, color: statusColor, flexShrink: 0,
              }}>
                {idx + 1}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, fontWeight: 500, color: "var(--text-primary)" }}>{ex.nodeName}</div>
                <div style={{ fontSize: 10, color: "var(--text-muted)", fontFamily: "'JetBrains Mono', monospace" }}>
                  {ex.nodeType} - {formatDuration(ex.duration)}
                </div>
              </div>
              <Tag color={statusColor} style={{ borderRadius: 4, fontSize: 10, lineHeight: "18px", margin: 0 }}>
                {RUN_STATUS_META[ex.status]?.label || ex.status}
              </Tag>
            </div>
            <div style={{
              height: 6, background: "#F1F5F9", borderRadius: 3,
              overflow: "hidden", marginLeft: 28,
            }}>
              <div style={{
                height: "100%", width: `${pct}%`,
                background: `linear-gradient(90deg, ${statusColor}, ${statusColor}99)`,
                borderRadius: 3, transition: "width 300ms ease",
              }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function RunDetailPage() {
  const { runId } = useParams<{ runId: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"dag" | "timeline">("dag");
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const loadRun = useCallback(async () => {
    if (!runId) return;
    setLoading(true);
    try {
      const data = await getRun(runId);
      setDetail(data);
      if (data.nodes.length > 0 && !selectedNodeId) {
        setSelectedNodeId(data.nodes[0].nodeId);
      }
    } catch {
      message.error("Failed to load run details");
    } finally {
      setLoading(false);
    }
  }, [runId]);

  useEffect(() => { loadRun(); }, [loadRun]);

 const handleRetry = async () => {
    Modal.confirm({
      title: "Retry this run?",
      content: "A new run will be created and executed from the beginning.",
      okText: "Yes, retry",
      okButtonProps: { icon: <ReloadOutlined /> },
      cancelText: "No",
      onOk: async () => {
    if (!runId) return;
    setActionLoading("retry");
    try {
      const result = await retryRun(runId);
      message.success("Retry initiated");
      navigate(`/runs/${result.newRunId}`);
    } catch {
      message.error("Failed to retry");
    } finally {
      setActionLoading(null);
    }
      },
    });
  };

 const handleCancel = async () => {
    Modal.confirm({
      title: "Cancel this run?",
      content: "The current execution will be stopped. In-progress nodes will be marked as canceled.",
      okText: "Yes, cancel",
      okButtonProps: { danger: true },
      cancelText: "No",
      onOk: async () => {
    if (!runId) return;
    setActionLoading("cancel");
    try {
      await cancelRun(runId);
      message.success("Run cancelled");
      loadRun();
    } catch {
      message.error("Failed to cancel");
    } finally {
      setActionLoading(null);
    }
      },
    });
 };
  const handleRetryFromNode = async (nodeId: string) => {
    if (!runId) return;
    setActionLoading("retryFromNode");
    try {
      const result = await retryFromNode(runId, nodeId);
      message.success("Retry from node initiated");
      navigate(`/runs/${result.newRunId}`);
    } catch {
      message.error("Failed to retry from node");
    } finally {
      setActionLoading(null);
    }
  };

  const selectedExecution = detail?.nodes.find((n: NodeExecution) => n.nodeId === selectedNodeId) || null;

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!detail) {
    return (
      <div style={{ padding: 32 }}>
        <Alert type="error" message="Run not found" description="Could not load this run's details." showIcon />
        <Button style={{ marginTop: 16 }} onClick={() => navigate("/runs")}>Back to Runs</Button>
      </div>
    );
  }

  const statusMeta = RUN_STATUS_META[detail.status] || { label: detail.status, color: "#6B7280" };
  const isTerminal = ["success", "failed", "canceled"].includes(detail.status);

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* Header */}
      <div style={{
        height: 52, background: "white",
        borderBottom: "1px solid #E2E8F0",
        display: "flex", alignItems: "center",
        padding: "0 20px", gap: 12, flexShrink: 0,
      }}>
        <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => navigate("/runs")} style={{ color: "#64748B" }} />
        <div style={{ fontFamily: "'DM Sans', system-ui", fontWeight: 600, fontSize: 14, color: "#0F172A" }}>
          Run #{detail.runId.slice(0, 8)}
        </div>
        <Tag color={statusMeta.color} style={{ borderRadius: 4, fontSize: 11, lineHeight: "20px" }}>
          {statusMeta.label}
        </Tag>
        <span style={{ fontSize: 12, color: "#94A3B8", fontFamily: "'JetBrains Mono', monospace" }}>
          {detail.workflowName}
        </span>
        <span style={{ fontSize: 12, color: "#94A3B8" }}>
          <ClockCircleOutlined style={{ marginRight: 4 }} />
          {formatDuration(detail.totalDuration)}
        </span>
        {detail.retryCount > 0 && (
          <Tag style={{ borderRadius: 4, fontSize: 11, background: "#FEF3C7", color: "#92400E", border: "1px solid #FDE68A" }}>
            Retry #{detail.retryCount}
          </Tag>
        )}

        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          {!isTerminal && detail.status !== "canceled" && (
            <Tooltip title="Cancel this run">
              <Button icon={<StopOutlined />} onClick={handleCancel} loading={actionLoading === "cancel"} size="small">
                Cancel
              </Button>
            </Tooltip>
          )}
          {(detail.status === "failed" || detail.status === "canceled") && (
            <Tooltip title="Retry this run from the beginning">
              <Button type="primary" icon={<ReloadOutlined />} onClick={handleRetry} loading={actionLoading === "retry"} size="small">
                Retry
              </Button>
            </Tooltip>
          )}
          <Button icon={<ReloadOutlined />} onClick={loadRun} size="small">Refresh</Button>
        </div>
      </div>

      {/* Content: DAG/Timeline + Node Detail */}
      <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
        {/* Left: DAG View or Timeline */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          {/* View mode switcher */}
          <div style={{
            padding: "8px 20px", background: "#FAFAFA",
            borderBottom: "1px solid #E2E8F0",
            display: "flex", alignItems: "center", gap: 12,
          }}>
            <Segmented
              value={viewMode}
              onChange={(val) => setViewMode(val as "dag" | "timeline")}
              options={[
                { label: <span><ApartmentOutlined /> DAG</span>, value: "dag" },
                { label: <span><UnorderedListOutlined /> Timeline</span>, value: "timeline" },
              ]}
              size="small"
            />
          </div>

          {/* Content area */}
          <div style={{ flex: 1, position: "relative" }}>
            {viewMode === "dag" ? (
              <RunDagView
                nodes={detail.nodes}
                selectedNodeId={selectedNodeId}
                onNodeSelect={setSelectedNodeId}
              />
            ) : (
              <TimelineView executions={detail.nodes} />
            )}
          </div>
        </div>

        {/* Right: Node Detail Panel */}
        <div style={{
          width: 360, flexShrink: 0,
          borderLeft: "1px solid #E2E8F0",
          background: "white",
          display: "flex", flexDirection: "column",
          overflow: "hidden",
        }}>
          <div style={{
            padding: "10px 16px", fontSize: 12, fontWeight: 600, color: "#64748B",
            borderBottom: "1px solid #E2E8F0",
            display: "flex", alignItems: "center", justifyContent: "space-between",
          }}>
            <span>Node Details</span>
            {selectedNodeId && (
              <Button
                type="text"
                size="small"
                icon={<RightOutlined />}
                onClick={() => setSelectedNodeId(null)}
                style={{ color: "#94A3B8" }}
              />
            )}
          </div>
          <div style={{ flex: 1, overflow: "auto" }}>
            <NodeExecutionDetail
              execution={selectedExecution}
              
              onRetryFromNode={handleRetryFromNode}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
