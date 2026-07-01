export function HUD() {
  return (
    <div
      className="animate-hud"
      style={{
        position: "absolute",
        bottom: 20,
        right: 20,
        zIndex: 10,
        background: "rgba(15,23,42,0.85)",
        backdropFilter: "blur(12px)",
        WebkitBackdropFilter: "blur(12px)",
        border: "1px solid rgba(148,163,184,0.15)",
        borderRadius: 10,
        padding: "10px 16px",
        display: "flex",
        alignItems: "center",
        gap: 14,
        fontSize: 12,
        color: "#94A3B8",
        boxShadow: "0 4px 24px rgba(0,0,0,0.3)",
      }}
    >
      <HudDot color="var(--success)" glow />
      <span>已保存</span>
      <HudDot color="var(--accent)" pulse />
      <span>自动</span>
      <span style={{ color: "#64748B" }}>节点: 3</span>
      <span style={{ color: "#64748B" }}>边: 2</span>
      <span style={{ cursor: "pointer", color: "var(--primary)" }}>↩</span>
      <span style={{ cursor: "pointer", color: "var(--text-muted)" }}>↪</span>
    </div>
  );
}

function HudDot({ color, glow, pulse }: { color: string; glow?: boolean; pulse?: boolean }) {
  return (
    <span
      style={{
        width: 6,
        height: 6,
        borderRadius: "50%",
        background: color,
        display: "inline-block",
        boxShadow: glow ? `0 0 6px ${color}` : undefined,
        animation: pulse ? "badge-pulse 1s ease-in-out infinite" : undefined,
      }}
    />
  );
}
