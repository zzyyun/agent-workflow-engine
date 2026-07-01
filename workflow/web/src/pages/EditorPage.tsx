import { useState, useCallback } from "react";
import { Button, Segmented } from "antd";
import { PlayCircleOutlined, ArrowLeftOutlined, SaveOutlined, CodeOutlined, AppstoreOutlined } from "@ant-design/icons";
import { useParams, useNavigate } from "react-router-dom";
import { EditorCanvas } from "../components/Canvas/EditorCanvas";
import { DslEditor } from "../components/Canvas/DslEditor";

export function EditorPage() {
  const { workflowId } = useParams();
  const navigate = useNavigate();
  const isNew = workflowId === "new";
  const [mode, setMode] = useState<"visual" | "dsl">("visual");
  const [dslValue, setDslValue] = useState("# DSL 编辑模式\n# 修改 YAML 后切换到可视化视图自动解析\n\nworkflow:\n  name: \"我的工作流\"\nnodes: []\nedges: []\n");

  const handleModeChange = useCallback((val: string | number) => {
    const newMode = val as "visual" | "dsl";
    setMode(newMode);
  }, []);

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
        <span style={{ fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 14, color: "var(--text-primary)" }}>
          {isNew ? "新建工作流" : "编辑工作流"}
        </span>
        <span style={{ color: "var(--text-muted)", fontSize: 12 }}>未保存</span>

        {/* Visual / DSL Tab Switcher */}
        <div style={{ marginLeft: 32 }}>
          <Segmented
            value={mode}
            onChange={handleModeChange}
            options={[
              { label: <span><AppstoreOutlined /> 可视化</span>, value: "visual" },
              { label: <span><CodeOutlined /> DSL</span>, value: "dsl" },
            ]}
            style={{ fontSize: 12 }}
          />
        </div>

        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <Button icon={<SaveOutlined />} style={{ fontSize: 12 }}>保存</Button>
          <Button type="primary" icon={<PlayCircleOutlined />} style={{ fontSize: 12, boxShadow: "var(--primary-glow)" }}>执行</Button>
        </div>
      </div>

      {/* Content: Canvas or DSL Editor */}
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        {mode === "visual" ? (
          <EditorCanvas onDslChange={setDslValue} />
        ) : (
          <div style={{ padding: 16, height: "100%", background: "var(--shell-bg)" }}>
            <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span>YAML 工作流定义 — 修改后切换到可视化视图自动解析</span>
                <Button size="small" type="primary" onClick={() => setMode("visual")}>应用并切回可视化</Button>
              </div>
              <div style={{ flex: 1 }}>
                <DslEditor value={dslValue} onChange={setDslValue} />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
