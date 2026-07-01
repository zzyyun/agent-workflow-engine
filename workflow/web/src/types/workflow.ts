/* ===== Agent Workflow Engine Types ===== */

export type NodeType =
  | 'llm'
  | 'tool'
  | 'condition'
  | 'loop'
  | 'retriever'
  | 'approval'
  | 'http'
  | 'subworkflow';

export type NodeStatus =
  | 'pending'
  | 'running'
  | 'success'
  | 'failed'
  | 'skipped'
  | 'waiting_approval'
  | 'canceled';

export type WorkflowStatus = 'published' | 'draft';
export type RunStatus = 'pending' | 'running' | 'success' | 'failed' | 'waiting_approval' | 'canceled';

export interface WorkflowNode {
  id: string;
  type: NodeType;
  label: string;
  position: { x: number; y: number };
  config: Record<string, any>;
  status?: NodeStatus;
}

export interface WorkflowEdge {
  source: string;
  target: string;
  label?: string;
  expression?: string;
}

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  status: WorkflowStatus;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  createdAt: string;
  updatedAt: string;
}

export interface WorkflowTemplate {
  id: string;
  name: string;
  description: string;
  category: 'business' | 'technical' | 'tutorial';
  nodeCount: number;
  estimatedTime: string;
  tags: string[];
}

export interface RunItem {
  runId: string;
  shortId: string;
  workflowName: string;
  status: RunStatus;
  triggerTime: string;
  duration: number;
}

export interface NodeExecution {
  nodeId: string;
  nodeName: string;
  nodeType: string;
  status: NodeStatus;
  input: Record<string, any>;
  output: Record<string, any> | null;
  error: string | null;
  duration: number;
  tokensUsed: number | null;
  startTime: string;
  endTime: string | null;
}

/* Node type metadata */
export const NODE_TYPE_META: Record<NodeType, {
  label: string;
  description: string;
  icon: string;
  color: string;
}> = {
  llm:      { label: 'LLM',       description: '大语言模型调用', icon: '🧠', color: 'var(--node-llm)' },
  tool:     { label: 'Tool',      description: '工具函数调用',   icon: '🔧', color: 'var(--node-tool)' },
  condition:{ label: 'Condition', description: '条件分支',      icon: '🔀', color: 'var(--node-condition)' },
  loop:     { label: 'Loop',      description: '循环迭代',      icon: '🔄', color: 'var(--node-loop)' },
  retriever:{ label: 'Retriever', description: '知识库检索',    icon: '🔍', color: 'var(--node-retriever)' },
  approval: { label: 'Approval',  description: '人工审批',      icon: '🛡️', color: 'var(--node-approval)' },
  http:     { label: 'HTTP',      description: 'HTTP 请求',     icon: '🌐', color: 'var(--node-http)' },
  subworkflow:{ label: 'SubFlow', description: '子流程',        icon: '📁', color: 'var(--node-subworkflow)' },
};

/* Node type to CSS class */
export const NODE_CSS_CLASS: Record<NodeType, string> = {
  llm: 'node-llm',
  tool: 'node-tool',
  condition: 'node-condition',
  loop: 'node-loop',
  retriever: 'node-retriever',
  approval: 'node-approval',
  http: 'node-http',
  subworkflow: 'node-subworkflow',
};

/* Status color mapping */
export const STATUS_COLORS: Record<NodeStatus, string> = {
  pending:         'var(--status-pending)',
  running:         'var(--status-running)',
  success:         'var(--status-success)',
  failed:          'var(--status-failed)',
  skipped:         'var(--status-skipped)',
  waiting_approval:'var(--status-waiting)',
  canceled:        'var(--status-canceled)',
};
