import { Button } from "antd";
import { PlusOutlined, AppstoreOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";

export function WorkflowListPage() {
  const navigate = useNavigate();
  return (
    <div style={{ padding: 32, height: "100%", overflow: "auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 700, color: "var(--text-primary)" }}>工作流</h1>
          <p style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 4 }}>管理你的 AI 自动化管线</p>
        </div>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/editor/new")}>新建工作流</Button>
      </div>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "60%", gap: 16 }}>
        <div style={{ width: 80, height: 80, borderRadius: 20, background: "linear-gradient(135deg, rgba(129,140,248,0.15), rgba(34,211,238,0.1))", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32 }}>⚡</div>
        <h3 style={{ fontFamily: "var(--font-display)", fontSize: 16, color: "var(--text-primary)", fontWeight: 600 }}>还没有工作流</h3>
        <p style={{ fontSize: 13, color: "var(--text-secondary)", maxWidth: 320, textAlign: "center", lineHeight: 1.6 }}>开始创建第一个工作流来体验 AI 自动化能力，从左侧面板拖拽节点、连线即可搭建管线。</p>
        <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate("/editor/new")} size="large">创建新工作流</Button>
          <Button icon={<AppstoreOutlined />} size="large">从模板创建</Button>
        </div>
      </div>
    </div>
  );
}
