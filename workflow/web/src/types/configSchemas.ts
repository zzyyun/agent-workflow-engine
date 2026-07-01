/* Node Config Form Fields */
export interface FormField {
  key: string;
  label: string;
  type: "text" | "textarea" | "number" | "slider" | "select" | "json" | "kv";
  required: boolean;
  defaultValue?: unknown;
  options?: { label: string; value: string }[];
}

export interface NodeConfigSchema {
  nodeType: string;
  fields: FormField[];
}

export const NODE_CONFIG_SCHEMAS: Record<string, FormField[]> = {
  llm: [
    { key: "system_prompt", label: "System Prompt", type: "textarea", required: true, defaultValue: "你是一个智能助手。" },
    { key: "model", label: "Model", type: "select", required: true, defaultValue: "mimo-v2.5", options: [{ label: "Mimo v2.5", value: "mimo-v2.5" }] },
    { key: "temperature", label: "Temperature", type: "slider", required: false, defaultValue: 0.7 },
    { key: "max_tokens", label: "Max Tokens", type: "number", required: false, defaultValue: 2048 },
  ],
  tool: [
    { key: "tool", label: "工具选择", type: "select", required: true, options: [{ label: "Webhook 发送", value: "webhook_sender" }, { label: "数据库查询", value: "db_query" }] },
    { key: "params", label: "参数映射", type: "json", required: false, defaultValue: {} },
  ],
  condition: [
    { key: "expression", label: "条件表达式", type: "text", required: true, defaultValue: "" },
  ],
  loop: [
    { key: "source", label: "迭代列表来源", type: "text", required: true, defaultValue: "" },
    { key: "variable", label: "循环变量名", type: "text", required: false, defaultValue: "item" },
    { key: "max_iterations", label: "最大迭代次数", type: "number", required: false, defaultValue: 10 },
  ],
  retriever: [
    { key: "knowledge_base", label: "知识库", type: "select", required: true, options: [{ label: "默认知识库", value: "default" }] },
    { key: "top_k", label: "TopK", type: "number", required: false, defaultValue: 5 },
    { key: "score_threshold", label: "Score Threshold", type: "slider", required: false, defaultValue: 0.7 },
  ],
  approval: [
    { key: "approver", label: "审批人", type: "text", required: true },
    { key: "timeout", label: "超时(小时)", type: "number", required: false, defaultValue: 24 },
    { key: "message_template", label: "审批消息模板", type: "textarea", required: false },
  ],
  http: [
    { key: "url", label: "URL", type: "text", required: true },
    { key: "method", label: "Method", type: "select", required: true, defaultValue: "GET", options: [{ label: "GET", value: "GET" }, { label: "POST", value: "POST" }, { label: "PUT", value: "PUT" }, { label: "DELETE", value: "DELETE" }] },
    { key: "headers", label: "Headers", type: "json", required: false, defaultValue: {} },
    { key: "body", label: "Body", type: "textarea", required: false },
  ],
  subworkflow: [
    { key: "workflow_id", label: "子工作流", type: "select", required: true, options: [] },
    { key: "input_mapping", label: "输入映射", type: "json", required: false, defaultValue: {} },
  ],
};
