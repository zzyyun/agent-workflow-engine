import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Input, Tag, message, Spin } from "antd";
import { SearchOutlined, AppstoreOutlined, ThunderboltOutlined, ClockCircleOutlined, ApartmentOutlined } from "@ant-design/icons";
import { listTemplates, createFromTemplate, type TemplateListResponse } from "../api/templates";

const CATEGORY_META: Record<string, { label: string; icon: string; color: string }> = {
  business:  { label: "Business",  icon: "💼", color: "#10B981" },
  technical: { label: "Technical", icon: "⚙️", color: "#3B82F6" },
  tutorial:  { label: "Tutorial",  icon: "📚", color: "#F59E0B" },
};

const TEMPLATE_ICONS: Record<string, string> = {
  "customer-support": "🎧",
  "daily-report": "📊",
  "data-pipeline": "🔄",
  "content-review": "✍️",
  "hello-world": "👋",
  "research-agent": "🔬",
};

const pageSize = 12;

export function TemplateMarketPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<TemplateListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string | undefined>();
  const [page, setPage] = useState(1);
  const [usingTemplate, setUsingTemplate] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listTemplates({
        category,
        search: search || undefined,
        page,
        size: pageSize,
      });
      setData(res);
    } catch {
      message.error("Failed to load templates");
    } finally {
      setLoading(false);
    }
  }, [category, search, page]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleUseTemplate = async (templateId: string, _templateName: string) => {
    setUsingTemplate(templateId);
    try {
      const result = await createFromTemplate(templateId);
      message.success(`Created: ${result.name}`);
      navigate(`/editor/${result.id}`);
    } catch {
      message.error("Failed to create from template");
    } finally {
      setUsingTemplate(null);
    }
  };

  const isEmpty = !loading && data && data.items.length === 0;

  return (
    <div style={{ padding: 32, height: "100%", overflow: "auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontFamily: "'DM Sans', system-ui", fontSize: 22, fontWeight: 700, color: "#0F172A", margin: 0, display: "flex", alignItems: "center", gap: 10 }}>
            <AppstoreOutlined style={{ color: "var(--primary)" }} />
            Template Market
          </h1>
          <p style={{ fontSize: 13, color: "#64748B", marginTop: 4 }}>
            Start faster with pre-built workflow templates
          </p>
        </div>
      </div>

      {/* Filters */}
      <div style={{ display: "flex", gap: 12, marginBottom: 24, alignItems: "center" }}>
        <Input
          prefix={<SearchOutlined style={{ color: "#94A3B8" }} />}
          placeholder="Search templates..."
          value={search}
          onChange={e => { setSearch(e.target.value); setPage(1); }}
          allowClear
          style={{ width: 280, borderRadius: 8 }}
        />
        <div style={{ display: "flex", gap: 6 }}>
          <Tag
            color={!category ? "blue" : "default"}
            style={{ borderRadius: 6, cursor: "pointer", padding: "2px 10px", fontSize: 12 }}
            onClick={() => { setCategory(undefined); setPage(1); }}
          >
            All
          </Tag>
          {Object.entries(CATEGORY_META).map(([key, meta]) => (
            <Tag
              key={key}
              color={category === key ? "blue" : "default"}
              style={{ borderRadius: 6, cursor: "pointer", padding: "2px 10px", fontSize: 12 }}
              onClick={() => { setCategory(key); setPage(1); }}
            >
              {meta.icon} {meta.label}
            </Tag>
          ))}
        </div>
      </div>

      {/* Template Grid */}
      {loading ? (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 300 }}>
          <Spin size="large" />
        </div>
      ) : isEmpty ? (
        <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: 300, gap: 12 }}>
          <div style={{ fontSize: 40, opacity: 0.3 }}><AppstoreOutlined /></div>
          <h3 style={{ fontSize: 16, color: "#64748B", fontWeight: 500 }}>No templates found</h3>
          <Button type="primary" onClick={() => navigate("/editor/new")}>Create from scratch</Button>
        </div>
      ) : (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: 16 }}>
            {data?.items.map((template) => {
              const catMeta = CATEGORY_META[template.category] || { label: template.category, icon: "📦", color: "#6B7280" };
              return (
                <div
                  key={template.id}
                  style={{
                    background: "white", borderRadius: 12,
                    border: "1px solid #E2E8F0",
                    padding: 20, cursor: "pointer",
                    transition: "all 200ms cubic-bezier(0.33,1,0.68,1)",
                    boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
                  }}
                  onMouseEnter={e => {
                    e.currentTarget.style.boxShadow = "0 4px 20px rgba(0,0,0,0.08)";
                    e.currentTarget.style.borderColor = "var(--primary)";
                    e.currentTarget.style.transform = "translateY(-2px)";
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.boxShadow = "0 1px 3px rgba(0,0,0,0.04)";
                    e.currentTarget.style.borderColor = "#E2E8F0";
                    e.currentTarget.style.transform = "translateY(0)";
                  }}
                >
                  {/* Icon + Category */}
                  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                    <div style={{
                      width: 40, height: 40, borderRadius: 10,
                      background: `${catMeta.color}15`,
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: 20,
                    }}>
                      {TEMPLATE_ICONS[template.id] || catMeta.icon}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 14, color: "#0F172A" }}>{template.name}</div>
                      <Tag color={catMeta.color} style={{ borderRadius: 4, fontSize: 10, lineHeight: "18px", margin: 0 }}>
                        {catMeta.label}
                      </Tag>
                    </div>
                  </div>

                  {/* Description */}
                  <p style={{ fontSize: 12, color: "#64748B", lineHeight: 1.6, margin: "0 0 12px 0" }}>
                    {template.description}
                  </p>

                  {/* Meta */}
                  <div style={{ display: "flex", gap: 12, fontSize: 11, color: "#94A3B8", marginBottom: 14 }}>
                    <span><ApartmentOutlined style={{ marginRight: 4 }} />{template.nodeCount} nodes</span>
                    <span><ClockCircleOutlined style={{ marginRight: 4 }} />{template.estimatedTime}</span>
                  </div>

                  {/* Tags + Action */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div style={{ display: "flex", gap: 4, flexWrap: "wrap" }}>
                      {(template.tags || []).slice(0, 3).map(tag => (
                        <Tag key={tag} style={{ borderRadius: 4, fontSize: 10, lineHeight: "18px", background: "#F1F5F9", color: "#475569", border: "none" }}>
                          {tag}
                        </Tag>
                      ))}
                    </div>
                    <Button
                      type="primary"
                      size="small"
                      icon={<ThunderboltOutlined />}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleUseTemplate(template.id, template.name);
                      }}
                      loading={usingTemplate === template.id}
                      style={{ borderRadius: 6, fontSize: 11 }}
                    >
                      Use
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination */}
          {data && data.total > pageSize && (
            <div style={{ display: "flex", justifyContent: "center", gap: 8, marginTop: 24 }}>
              {Array.from({ length: Math.ceil(data.total / pageSize) }, (_, i) => i + 1).map(p => (
                <Button
                  key={p}
                  size="small"
                  type={p === page ? "primary" : "default"}
                  onClick={() => setPage(p)}
                  style={{ minWidth: 32 }}
                >
                  {p}
                </Button>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
