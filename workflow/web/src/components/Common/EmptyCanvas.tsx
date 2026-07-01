export function EmptyCanvas({ visible }: { visible: boolean }) {
  if (!visible) return null;
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 2,
        pointerEvents: "none",
      }}
    >
      <svg viewBox="0 0 200 120" width={200} height={120}>
        <defs>
          <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#818CF8" stopOpacity="0.8"/>
            <stop offset="100%" stopColor="#818CF8" stopOpacity="0.3"/>
          </linearGradient>
        </defs>
        <rect x="10" y="48" width="44" height="24" rx="8" fill="#1E293B" stroke="#818CF8" strokeWidth="1.5"/>
        <text x="32" y="63" textAnchor="middle" fill="#818CF8" fontSize="9" fontFamily="Inter">📊 数据源</text>
        <rect x="78" y="48" width="44" height="24" rx="8" fill="#1E293B" stroke="#34D399" strokeWidth="1.5"/>
        <text x="100" y="63" textAnchor="middle" fill="#34D399" fontSize="9" fontFamily="Inter">🤖 LLM</text>
        <rect x="146" y="48" width="44" height="24" rx="8" fill="#1E293B" stroke="#FBBF24" strokeWidth="1.5"/>
        <text x="168" y="63" textAnchor="middle" fill="#FBBF24" fontSize="9" fontFamily="Inter">📬 输出</text>
        <line x1="54" y1="60" x2="78" y2="60" stroke="rgba(129,140,248,0.3)" strokeWidth="1.5"/>
        <line x1="122" y1="60" x2="146" y2="60" stroke="rgba(52,211,153,0.3)" strokeWidth="1.5"/>
      </svg>
      <h3 style={{ fontFamily: "var(--font-display)", fontSize: 16, color: "#CBD5E1", marginBottom: 8 }}>你的第一个工作流</h3>
      <p style={{ fontSize: 13, color: "#64748B" }}>从左侧面板拖拽节点到画布，连线搭建自动化管线</p>
    </div>
  );
}
