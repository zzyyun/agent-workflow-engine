import { useState } from "react";
import { Button, Input, Card, message, Divider, Switch } from "antd";
import { KeyOutlined, SettingOutlined, InfoCircleOutlined, GithubOutlined } from "@ant-design/icons";

export function SettingsPage() {
  const [apiKey, setApiKey] = useState(localStorage.getItem("api_key") || "");
  const [saving, setSaving] = useState(false);

  const handleSaveApiKey = async () => {
    setSaving(true);
    try {
      localStorage.setItem("api_key", apiKey);
      await new Promise(r => setTimeout(r, 300));
      message.success("API Key saved");
    } catch {
      message.error("Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const handleClearApiKey = () => {
    setApiKey("");
    localStorage.removeItem("api_key");
    message.success("API Key cleared");
  };

  return (
    <div style={{ padding: 32, height: "100%", overflow: "auto", maxWidth: 640 }}>
      <h1 style={{ fontFamily: "'DM Sans', system-ui", fontSize: 22, fontWeight: 700, color: "#0F172A", margin: "0 0 24px 0", display: "flex", alignItems: "center", gap: 10 }}>
        <SettingOutlined style={{ color: "var(--primary)" }} />
        Settings
      </h1>

      {/* API Key */}
      <Card
        size="small"
        style={{ borderRadius: 10, marginBottom: 16, border: "1px solid #E2E8F0" }}
        bodyStyle={{ padding: 20 }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
          <KeyOutlined style={{ color: "var(--primary)", fontSize: 16 }} />
          <span style={{ fontWeight: 600, fontSize: 14, color: "#0F172A" }}>API Key</span>
        </div>
        <p style={{ fontSize: 12, color: "#64748B", margin: "0 0 12px 0", lineHeight: 1.5 }}>
          Your API key is stored locally and sent with each request. It is never shared with third parties.
        </p>
        <Input.Password
          value={apiKey}
          onChange={e => setApiKey(e.target.value)}
          placeholder="sk-..."
          style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, borderRadius: 6, marginBottom: 12 }}
          visibilityToggle={false}
        />
        <div style={{ display: "flex", gap: 8 }}>
          <Button type="primary" onClick={handleSaveApiKey} loading={saving} size="small">
            Save
          </Button>
          {apiKey && (
            <Button danger onClick={handleClearApiKey} size="small">
              Clear
            </Button>
          )}
        </div>
      </Card>

      {/* Preferences */}
      <Card
        size="small"
        style={{ borderRadius: 10, marginBottom: 16, border: "1px solid #E2E8F0" }}
        bodyStyle={{ padding: 20 }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
          <SettingOutlined style={{ color: "var(--primary)", fontSize: 16 }} />
          <span style={{ fontWeight: 600, fontSize: 14, color: "#0F172A" }}>Preferences</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <div style={{ fontSize: 13, color: "#0F172A" }}>Dark Mode</div>
            <div style={{ fontSize: 11, color: "#94A3B8" }}>Coming soon</div>
          </div>
          <Switch disabled />
        </div>
      </Card>

      {/* About */}
      <Card
        size="small"
        style={{ borderRadius: 10, border: "1px solid #E2E8F0" }}
        bodyStyle={{ padding: 20 }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
          <InfoCircleOutlined style={{ color: "var(--primary)", fontSize: 16 }} />
          <span style={{ fontWeight: 600, fontSize: 14, color: "#0F172A" }}>About</span>
        </div>
        <div style={{ fontSize: 13, color: "#475569", lineHeight: 1.8 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>Version</span>
            <span style={{ fontFamily: "'JetBrains Mono', monospace", color: "#94A3B8" }}>0.1.0</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>Framework</span>
            <span>React 19 + Vite 8</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <span>UI Library</span>
            <span>Ant Design 6</span>
          </div>
          <Divider style={{ margin: "8px 0" }} />
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span>GitHub</span>
            <Button
              type="link"
              size="small"
              icon={<GithubOutlined />}
              href="https://github.com/zzyyun/agent-workflow-engine"
              target="_blank"
              style={{ fontSize: 12 }}
            >
              zzyyun/agent-workflow-engine
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}
