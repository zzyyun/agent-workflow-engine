import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Table, Tag, Space, Input, Select, message, Tooltip } from "antd";
import { ThunderboltOutlined, ReloadOutlined, ClockCircleOutlined, RightOutlined } from "@ant-design/icons";
import { listRuns, type RunItem } from "../api/runs";
import { TriggerRunModal } from "../components/Runs/TriggerRunModal";


const RUN_STATUS_META: Record<string, { label: string; color: string }> = {
  pending:         { label: "Pending",     color: "#FBBF24" },
  running:         { label: "Running",     color: "#3B82F6" },
  success:         { label: "Success",     color: "#10B981" },
  failed:          { label: "Failed",      color: "#EF4444" },
  waiting_approval:{ label: "Waiting",     color: "#F59E0B" },
  canceled:        { label: "Canceled",    color: "#6B7280" },
};

function statusTag(s: string) {
  const m = RUN_STATUS_META[s] || { label: s, color: "#6B7280" };
  return <Tag color={m.color} style={{ borderRadius: 4, fontSize: 12 }}>{m.label}</Tag>;
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
}

export function RunListPage() {
  const navigate = useNavigate();
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [triggerOpen, setTriggerOpen] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listRuns({
        workflowId: search || undefined,
        status: statusFilter,
        page,
        size: 20,
      });
      setRuns(res.items);
      setTotal(res.total);
    } catch {
      message.error("Failed to load run history");
    } finally {
      setLoading(false);
    }
  }, [search, statusFilter, page]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleTriggerSuccess = (runId: string) => {
    loadData();
    navigate(`/runs/${runId}`);
  };

  const isEmpty = !loading && runs.length === 0 && !search && !statusFilter;

  const columns = [
    {
      title: "Run ID",
      dataIndex: "shortId",
      key: "shortId",
      width: 120,
      render: (id: string) => (
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: "var(--text-secondary)" }}>
          #{id}
        </span>
      ),
    },
    {
      title: "Workflow",
      dataIndex: "workflowName",
      key: "workflowName",
      render: (name: string) => (
        <span style={{ fontWeight: 500, color: "var(--text-primary)" }}>{name}</span>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 120,
      render: (s: string) => statusTag(s),
    },
    {
      title: "Trigger Time",
      dataIndex: "triggerTime",
      key: "triggerTime",
      width: 180,
      render: (t: string) => (
        <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
          <ClockCircleOutlined style={{ marginRight: 6, fontSize: 11, color: "var(--text-muted)" }} />
          {new Date(t).toLocaleString()}
        </span>
      ),
    },
    {
      title: "Duration",
      dataIndex: "duration",
      key: "duration",
      width: 100,
      render: (d: number) => (
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: d > 30000 ? "#EF4444" : "var(--text-secondary)" }}>
          {formatDuration(d)}
        </span>
      ),
    },
    {
      title: "",
      key: "actions",
      width: 60,
      render: (_: unknown, r: RunItem) => (
        <Tooltip title="View Details">
          <Button
            type="text"
            size="small"
            icon={<RightOutlined />}
            onClick={() => navigate(`/runs/${r.runId}`)}
          />
        </Tooltip>
      ),
    },
  ];

  return (
    <div style={{ padding: 32, height: "100%", overflow: "auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 700, color: "var(--text-primary)", margin: 0, display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ color: "var(--primary)" }}>
              <ThunderboltOutlined />
            </span>
            Task Runs
          </h1>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>
            Monitor and manage your workflow executions
          </p>
        </div>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={loadData}>Refresh</Button>
          <Button type="primary" icon={<ThunderboltOutlined />} onClick={() => setTriggerOpen(true)} style={{ boxShadow: "var(--primary-glow)" }}>
            Trigger Run
          </Button>
        </Space>
      </div>

      {/* Filters */}
      {!isEmpty && (
        <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
          <Input.Search
            placeholder="Search by workflow name..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            onSearch={v => setSearch(v)}
            allowClear
            style={{ width: 280 }}
          />
          <Select
            placeholder="Status filter"
            value={statusFilter}
            onChange={v => setStatusFilter(v)}
            allowClear
            style={{ width: 140 }}
            options={Object.entries(RUN_STATUS_META).map(([k, v]) => ({ label: v.label, value: k }))}
          />
        </div>
      )}

      {/* Empty State */}
      {isEmpty ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "60%", gap: 16 }}>
          <div style={{
            width: 80, height: 80, borderRadius: 20,
            background: "linear-gradient(135deg, rgba(129,140,248,0.15), rgba(34,211,238,0.1))",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32,
          }}>
            <ThunderboltOutlined style={{ color: "var(--primary)" }} />
          </div>
          <h3 style={{ fontFamily: "var(--font-display)", fontSize: 16, color: "var(--text-primary)", fontWeight: 600, margin: 0 }}>
            No runs yet
          </h3>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", maxWidth: 360, textAlign: "center", lineHeight: 1.6 }}>
            Trigger your first workflow run to see execution history. Each run will be tracked with status, duration, and node-level details.
          </p>
          <Button type="primary" icon={<ThunderboltOutlined />} onClick={() => setTriggerOpen(true)} size="large" style={{ boxShadow: "var(--primary-glow)", marginTop: 8 }}>
            Trigger First Run
          </Button>
        </div>
      ) : (
        <Table
          dataSource={runs}
          columns={columns}
          rowKey="runId"
          loading={loading}
          pagination={{
            current: page,
            total,
            pageSize: 20,
            onChange: setPage,
            showTotal: (t: number) => `${t} total runs`,
          }}
          size="middle"
          style={{ fontSize: 13 }}
          onRow={(r: RunItem) => ({
            onClick: () => navigate(`/runs/${r.runId}`),
            style: { cursor: "pointer" },
          })}
        />
      )}

      {/* Trigger Run Modal */}
      <TriggerRunModal
        open={triggerOpen}
        onClose={() => setTriggerOpen(false)}
        onSuccess={handleTriggerSuccess}
      />
    </div>
  );
}
