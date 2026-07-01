import client from "./client";

export interface RunItem {
  runId: string;
  shortId: string;
  workflowName: string;
  status: string;
  triggerTime: string;
  duration: number;
}

export interface RunListResponse {
  items: RunItem[];
  total: number;
  page: number;
}

export interface NodeExecution {
  nodeId: string;
  nodeName: string;
  nodeType: string;
  status: string;
  input: Record<string, any>;
  output: Record<string, any> | null;
  error: string | null;
  duration: number;
  tokensUsed: number | null;
  startTime: string;
  endTime: string | null;
}

export interface RunDetail {
  runId: string;
  workflowName: string;
  status: string;
  totalDuration: number;
  retryCount: number;
  triggerTime: string;
  nodes: NodeExecution[];
}

export async function triggerRun(workflowId: string, input?: Record<string, any>): Promise<{ runId: string }> {
  const res = await client.post("/runs", { workflowId, input });
  return res.data;
}

export async function listRuns(params?: {
  workflowId?: string;
  status?: string;
  from?: string;
  to?: string;
  page?: number;
  size?: number;
}): Promise<RunListResponse> {
  const res = await client.get("/runs", { params });
  return res.data;
}

export async function getRun(runId: string): Promise<RunDetail> {
  const res = await client.get(`/runs/${runId}`);
  return res.data;
}

export async function retryRun(runId: string): Promise<{ newRunId: string }> {
  const res = await client.post(`/runs/${runId}/retry`);
  return res.data;
}

export async function retryFromNode(runId: string, nodeId: string): Promise<{ newRunId: string }> {
  const res = await client.post(`/runs/${runId}/retry-from/${nodeId}`);
  return res.data;
}

export async function cancelRun(runId: string): Promise<void> {
  await client.post(`/runs/${runId}/cancel`);
}
