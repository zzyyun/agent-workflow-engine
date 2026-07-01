import { useState } from "react";
import { Button, Form, Input, message } from "antd";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../store/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login, loading } = useAuth();
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (values: { username: string; password: string }) => {
    setError(null);
    try {
      await login(values.username, values.password);
      message.success("登录成功");
      navigate("/workflows");
    } catch (err: unknown) {
      const apiErr = err as { response?: { data?: { message?: string } } };
      const msg = apiErr?.response?.data?.message || "登录失败，请检查用户名和密码";
      setError(msg);
    }
  };

  return (
    <div style={{
      height: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "linear-gradient(135deg, #0F172A 0%, #1E293B 100%)",
      position: "relative", overflow: "hidden",
    }}>
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
          <h1 style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 22, fontWeight: 700, color: "white", margin: 0 }}>
            Agent<span style={{ color: "var(--primary)" }}>Workflow</span>
          </h1>
          <p style={{ color: "#64748B", fontSize: 13, marginTop: 4 }}>AI Agent 工作流引擎</p>
        </div>
        {error && (
          <div style={{ padding: "8px 12px", background: "rgba(251,113,133,0.15)", border: "1px solid rgba(251,113,133,0.3)", borderRadius: 8, marginBottom: 16, fontSize: 12, color: "#FB7185" }}>
            {error}
          </div>
        )}
        <Form layout="vertical" onFinish={handleSubmit}>
          <Form.Item label={<span style={{ color: "#CBD5E1", fontSize: 12 }}>用户名</span>} name="username" rules={[{ required: true, message: "请输入用户名" }]}>
            <Input placeholder="输入用户名" style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", color: "white", borderRadius: 8, height: 40 }} />
          </Form.Item>
          <Form.Item label={<span style={{ color: "#CBD5E1", fontSize: 12 }}>密码</span>} name="password" rules={[{ required: true, message: "请输入密码" }]}>
            <Input.Password placeholder="输入密码" style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", color: "white", borderRadius: 8, height: 40 }} />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block size="large" loading={loading}
              style={{ height: 42, borderRadius: 8, fontSize: 14, fontWeight: 600, boxShadow: "0 0 24px rgba(129,140,248,0.5)" }}>
              登录
            </Button>
          </Form.Item>
        </Form>
      </div>
    </div>
  );
}
