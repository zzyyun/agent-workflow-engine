export const NODE_META: Record<string, { label: string; desc: string; icon: string }> = {
  llm: { label: "LLM", desc: "大语言模型调用", icon: "🧠" },
  tool: { label: "Tool", desc: "工具函数调用", icon: "🔧" },
  condition: { label: "Condition", desc: "条件分支", icon: "🔀" },
  loop: { label: "Loop", desc: "循环迭代", icon: "🔄" },
  retriever: { label: "Retriever", desc: "知识库检索", icon: "🔍" },
  approval: { label: "Approval", desc: "人工审批", icon: "🛡️" },
  http: { label: "HTTP", desc: "HTTP 请求", icon: "🌐" },
  subworkflow: { label: "SubFlow", desc: "子流程", icon: "📁" },
};
