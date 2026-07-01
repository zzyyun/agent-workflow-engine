import { Button } from "antd";
import { PlayCircleOutlined, ArrowLeftOutlined, SaveOutlined } from "@ant-design/icons";
import { useParams, useNavigate } from "react-router-dom";
import { EditorCanvas } from "../components/Canvas/EditorCanvas";

export function EditorPage() {
  const { workflowId } = useParams();
  const navigate = useNavigate();
  const isNew = workflowId === "new";
  const title = isNew ? "新建工作流" : "编辑工作流";

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      {/* Toolbar */}
      <div style={{
        height: 44, background: "var(--shell-surface)",
        borderBottom: "1px solid var(--shell-border)",
        display: "flex", alignItems: "center",
        padding: "0 16px", gap: 8, fontSize: 13, flexShrink: 0,
      }}>
        <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => navigate("/workflows")} style={{ color: "var(--text-secondary)" }} />
        <span style={{ fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 14, color: "var(--text-primary)" }}>{title}</span>
        <span style={{ color: "var(--text-muted)", fontSize: 12 }}>未保存</span>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <Button icon={<SaveOutlined />} style={{ fontSize: 12 }}>保存</Button>
          <Button type="primary" icon={<PlayCircleOutlined />} style={{ fontSize: 12, boxShadow: "var(--primary-glow)" }}>执行</Button>
        </div>
      </div>
      {/* Canvas */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        <EditorCanvas />
      </div>
    </div>
  );
}
