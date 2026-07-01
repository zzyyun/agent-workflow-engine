import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const NAV_ITEMS = [
  { label: "Workflows", path: "/workflows" },
  { label: "Runs", path: "/runs" },
  { label: "Templates", path: null },
  { label: "Docs", path: null },
];

export function TopNav() {
  const location = useLocation();
  const navigate = useNavigate();
// const isEditor = location.pathname.startsWith("/editor");
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav style={{
      height: "var(--nav-height)", background: "var(--shell-surface)",
      borderBottom: "1px solid var(--shell-border)",
      display: "flex", alignItems: "center",
      padding: "0 16px", gap: 20, fontSize: 13,
      zIndex: 100, position: "relative",
    }}>
      <div
        onClick={() => navigate("/workflows")}
        style={{
          fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 15,
          display: "flex", alignItems: "center", gap: 8,
          cursor: "pointer", color: "var(--text-primary)",
        }}
      >
        <span style={{ color: "var(--primary)" }}>+</span>
        Agent<span style={{ color: "var(--primary)" }}>Workflow</span>
      </div>

      <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
        {NAV_ITEMS.map((item) => {
          const active = item.path ? location.pathname.startsWith(item.path) : false;
          return (
            <a
              key={item.label}
              onClick={() => item.path && navigate(item.path)}
              style={{
                color: active ? "var(--text-primary)" : "var(--text-secondary)",
                fontWeight: active ? 500 : 400,
                cursor: item.path ? "pointer" : "default",
                padding: "2px 8px",
                borderRadius: 4,
                textDecoration: "none",
                transition: "all 200ms cubic-bezier(0.33,1,0.68,1)",
                opacity: item.path ? 1 : 0.5,
              }}
            >
              {item.label}
            </a>
          );
        })}
      </div>

      <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 12, color: "var(--text-muted)" }}>v0.1.0</span>
        <div
          onClick={() => setMenuOpen(!menuOpen)}
          style={{
            width: 28, height: 28, borderRadius: "50%",
            background: "linear-gradient(135deg, var(--primary), var(--accent))",
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "white", fontSize: 12, fontWeight: 600, cursor: "pointer",
            position: "relative",
          }}
        >
          Y
          {menuOpen && (
            <div style={{
              position: "absolute", top: 36, right: 0,
              background: "var(--shell-surface)",
              border: "1px solid var(--shell-border)", borderRadius: 8,
              boxShadow: "0 4px 24px rgba(0,0,0,0.06)",
              padding: "4px 0", minWidth: 140, zIndex: 200,
            }}>
              {["Settings", "API Key", "Logout"].map((item) => (
                <div
                  key={item}
                  style={{ padding: "8px 16px", cursor: "pointer", fontSize: 13, transition: "background 150ms" }}
                  onMouseEnter={(e) => e.currentTarget.style.background = "#F1F5F9"}
                  onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
                >
                  {item}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
