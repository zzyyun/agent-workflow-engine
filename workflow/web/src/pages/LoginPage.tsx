import { Button, Form, Input } from "antd";
import { useNavigate } from "react-router-dom";

export function LoginPage() {
  const navigate = useNavigate();

  return (
    <div style={{
      height: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "linear-gradient(135deg, #0F172A 0%, #1E293B 100%)",
      position: "relative", overflow: "hidden",
    }}>
      {/* Ambient glow */}
      <div style={{
        position: "absolute", width: 400, height: 400, borderRadius: "50%",
        background: "radial-gradient(circle, rgba(129,140,248,0.15) 0%, transparent 70%)",
        top: "20%", left: "50%", transform: "translateX(-50%)",
      }} />
      
      <div style={{
        width: 380, padding: "40px 36px", borderRadius: 16,
        background: "rgba(255,255,255,0.04)", backdropFilter: "blur(20px)",
        border: "1px solid rgba(255,255,255,0.08)",
        position: "relative", zIndex: 1,
      }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>⚡</div>
          <h1 style={{
            fontFamily: "var(--font-display)", fontSize: 22, fontWeight: 700,
            color: "white", margin: 0,
          }}>
            Agent<span style={{ color: "var(--primary)" }}>Workflow</span>
          </h1>
          <p style={{ color: "#64748B", fontSize: 13, marginTop: 4 }}>AI Agent 工作流引擎</p>
        </div>
        <Form layout="vertical" onFinish={() => navigate("/workflows")}>
          <Form.Item label={<span style={{ color: "#CBD5E1", fontSize: 12 }}>用户名</span>} name="username">
            <Input placeholder="输入用户名" style={{
              background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)",
              color: "white", borderRadius: 8, height: 40,
            }} />
          </Form.Item>
          <Form.Item label={<span style={{ color: "#CBD5E1", fontSize: 12 }}>密码</span>} name="password">
            <Input.Password placeholder="输入密码" style={{
              background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)",
              color: "white", borderRadius: 8, height: 40,
            }} />
          </Form.Item>
          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              size="large"
              style={{
                height: 42, borderRadius: 8, fontSize: 14, fontWeight: 600,
                boxShadow: "var(--primary-glow)",
              }}
            >
              登录
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
}
