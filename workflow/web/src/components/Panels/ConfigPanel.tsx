import { useState } from "react";
import { Input, InputNumber, Select, Slider } from "antd";
import { NODE_CONFIG_SCHEMAS } from "../../types/configSchemas";

interface ConfigPanelProps { nodeType: string }

export function ConfigPanel({ nodeType }: ConfigPanelProps) {
  const fields = NODE_CONFIG_SCHEMAS[nodeType] || [];
  const [values, setValues] = useState<Record<string, unknown>>(() => {
    const init: Record<string, unknown> = {};
    fields.forEach(f => { init[f.key] = f.defaultValue ?? ""; });
    return init;
  });
  const update = (k: string, v: unknown) => setValues(p => ({ ...p, [k]: v }));
  if (!fields.length) return <div style={{ padding: 24, textAlign: "center", color: "var(--text-muted)", fontSize: 13 }}>该节点类型没有可配置参数</div>;
  return (<div style={{ padding: 16, display: "flex", flexDirection: "column", gap: 14, fontSize: 13 }}>
    {fields.map(f => (<div key={f.key}><label style={{ fontSize: 11, color: "var(--text-secondary)", display: "block", marginBottom: 4 }}>{f.label}{f.required && <span style={{ color: "var(--error)", marginLeft: 2 }}>*</span>}</label>
      {f.type === "textarea" && <Input.TextArea value={String(values[f.key] ?? "")} onChange={e => update(f.key, e.target.value)} rows={4} style={{ fontSize: 12, fontFamily: "var(--font-code)" }} />}
      {(f.type === "text") && <Input value={String(values[f.key] ?? "")} onChange={e => update(f.key, e.target.value)} style={{ fontSize: 13 }} />}
      {f.type === "number" && <InputNumber value={values[f.key] as number} onChange={v => update(f.key, v)} style={{ width: "100%", fontSize: 13 }} />}
      {f.type === "slider" && <div><Slider value={values[f.key] as number} onChange={v => update(f.key, v)} min={0} max={2} step={0.1} /><div style={{ textAlign: "center", fontSize: 12, color: "var(--text-secondary)" }}>{String(values[f.key])}</div></div>}
      {f.type === "select" && f.options && <Select value={values[f.key] as string} onChange={v => update(f.key, v)} options={f.options} style={{ width: "100%", fontSize: 13 }} />}
      {f.type === "json" && <Input.TextArea value={JSON.stringify(values[f.key], null, 2)} onChange={e => { try { update(f.key, JSON.parse(e.target.value)); } catch {} }} rows={4} style={{ fontSize: 11, fontFamily: "var(--font-code)" }} />}
    </div>))}
    <div style={{ display: "flex", gap: 8, marginTop: 8, borderTop: "1px solid var(--shell-border)", paddingTop: 12 }}>
      <button style={{ flex: 1, padding: 8, background: "var(--primary)", color: "white", border: "none", borderRadius: 6, fontSize: 12, fontWeight: 500, cursor: "pointer", fontFamily: "var(--font-body)", boxShadow: "var(--primary-glow)" }}>保存</button>
      <button style={{ padding: "8px 12px", background: "transparent", color: "var(--text-secondary)", border: "1px solid var(--shell-border)", borderRadius: 6, fontSize: 12, cursor: "pointer", fontFamily: "var(--font-body)" }}>取消</button>
    </div>
  </div>);
}
