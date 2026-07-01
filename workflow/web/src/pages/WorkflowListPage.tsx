import { useState, useEffect, useCallback } from "react";
import { Button, Table, Input, Select, Space, Modal, message, Tag, Upload } from "antd";
import { PlusOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined, DownloadOutlined, UploadOutlined, AppstoreOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { listWorkflows, deleteWorkflow, exportWorkflow, importWorkflow, type Workflow } from "../api/workflows";

export function WorkflowListPage() {
  const navigate = useNavigate();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listWorkflows({ search, status: statusFilter, page, size: 20 });
      setWorkflows(res.items);
      setTotal(res.total);
    } catch {
      message.error("加载工作流列表失败");
    } finally { setLoading(false); }
  }, [search, statusFilter, page]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleDelete = async (id: string) => {
    try {
      await deleteWorkflow(id);
      message.success("已删除");
      setDeleteConfirm(null);
      loadData();
    } catch { message.error("删除失败"); }
  };

  const handleExport = async (id: string, name: string) => {
    try {
      const data = await exportWorkflow(id);
      const blob = new Blob([data.yaml], { type: "text/yaml" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a"); a.href = url; a.download = `${name}.yaml`; a.click();
      URL.revokeObjectURL(url);
    } catch { message.error("导出失败"); }
  };

  const handleImport = async (file: File) => {
    try {
      const text = await file.text();
      const wf = await importWorkflow(text);
      message.success(`已导入：${wf.name}`);
      loadData();
    } catch (err: unknown) {
      const apiErr = err as { response?: { data?: { message?: string } } };
      message.error(apiErr?.response?.data?.message || "导入失败");
    }
    return false; // prevent upload
  };

  const columns = [
    { title: "名称", dataIndex: "name", key: "name", render: (n: string, r: Workflow) => <a onClick={() => navigate(`/editor/${r.id}`)} style={{ fontWeight: 500 }}>{n}</a> },
    { title: "节点", dataIndex: "nodeCount", key: "nodeCount", width: 80 },
    { title: "状态", dataIndex: "status", key: "status", width: 100, render: (s: string) => <Tag color={s === "published" ? "green" : "default"}>{s === "published" ? "已发布" : "草稿"}</Tag> },
    { title: "更新", dataIndex: "updatedAt", key: "updatedAt", width: 160, render: (d: string) => new Date(d).toLocaleString() },
    { title: "", key: "actions", width: 200, render: (_: unknown, r: Workflow) => (
      <Space size={4}>
        <Button type="text" size="small" icon={<EditOutlined />} onClick={() => navigate(`/editor/${r.id}`)} title="编辑" />
        <Button type="text" size="small" icon={<PlayCircleOutlined />} title="执行" />
        <Button type="text" size="small" icon={<DownloadOutlined />} onClick={() => handleExport(r.id, r.name)} title="导出 YAML" />
        <Button type="text" size="small" danger icon={<DeleteOutlined />} onClick={() => setDeleteConfirm(r.id)} title="删除" />
      </Space>
    )},
  ];

  const isEmpty = !loading && workflows.length === 0 && !search && !statusFilter;

  return (
    <div style={{ padding: 32, height: "100%", overflow: "auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 700, color: "var(--text-primary)", margin: 0 }}>工作流</h1>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>管理你的 AI 自动化管线</p>
        </div>
        <Space>
          <Upload accept=".yaml,.yml" showUploadList={false} beforeUpload={handleImport}>
            <Button icon={<UploadOutlined />}>导入 YAML</Button>
          </Upload>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/editor/new")}>新建工作流</Button>
        </Space>
      </div>

      {/* Filters */}
      {!isEmpty && <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
        <Input.Search placeholder="搜索工作流..." value={search} onChange={e => setSearch(e.target.value)} onSearch={v => setSearch(v)} allowClear style={{ width: 280 }} />
        <Select placeholder="状态筛选" value={statusFilter} onChange={v => setStatusFilter(v)} allowClear style={{ width: 140 }} options={[{ label: "已发布", value: "published" }, { label: "草稿", value: "draft" }]} />
      </div>}

      {/* Empty State */}
      {isEmpty ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "60%", gap: 16 }}>
          <div style={{ width: 80, height: 80, borderRadius: 20, background: "linear-gradient(135deg, rgba(129,140,248,0.15), rgba(34,211,238,0.1))", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32 }}>⚡</div>
          <h3 style={{ fontFamily: "var(--font-display)", fontSize: 16, color: "var(--text-primary)", fontWeight: 600, margin: 0 }}>还没有工作流</h3>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", maxWidth: 320, textAlign: "center", lineHeight: 1.6 }}>开始创建第一个工作流来体验 AI 自动化能力，从左侧面板拖拽节点、连线即可搭建管线。</p>
          <Space size={12} style={{ marginTop: 8 }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/editor/new")} size="large">创建新工作流</Button>
            <Button icon={<AppstoreOutlined />} size="large">从模板创建</Button>
          </Space>
        </div>
      ) : (
        <Table dataSource={workflows} columns={columns} rowKey="id" loading={loading} pagination={{ current: page, total, pageSize: 20, onChange: setPage }} size="middle" />
      )}

      {/* Delete confirm */}
      <Modal open={!!deleteConfirm} onCancel={() => setDeleteConfirm(null)} onOk={() => deleteConfirm && handleDelete(deleteConfirm)} title="确认删除" okText="删除" okButtonProps={{ danger: true }} cancelText="取消">
        <p>删除后无法恢复，确定要删除该工作流吗？</p>
      </Modal>
    </div>
  );
}
