import client from "./client";

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodeCount: number;
  status: "published" | "draft";
  updatedAt: string;
  createdAt: string;
}

export interface WorkflowListResponse {
  items: Workflow[];
  total: number;
  page: number;
}

export interface WorkflowDetail extends Workflow {
  yaml: string;
}

export async function listWorkflows(params?: {
  search?: string;
  status?: string;
  page?: number;
  size?: number;
}): Promise<WorkflowListResponse> {
  const res = await client.get<WorkflowListResponse>("/workflows", { params });
  return res.data;
}

export async function getWorkflow(id: string): Promise<WorkflowDetail> {
  const res = await client.get<WorkflowDetail>(`/workflows/${id}`);
  return res.data;
}

export async function createWorkflow(data: { name: string; description?: string; yaml: string }): Promise<Workflow> {
  const res = await client.post<Workflow>("/workflows", data);
  return res.data;
}

export async function updateWorkflow(id: string, data: { name?: string; description?: string; yaml?: string }): Promise<Workflow> {
  const res = await client.put<Workflow>(`/workflows/${id}`, data);
  return res.data;
}

export async function deleteWorkflow(id: string): Promise<void> {
  await client.delete(`/workflows/${id}`);
}

export async function exportWorkflow(id: string): Promise<{ yaml: string; filename: string }> {
  const res = await client.get(`/workflows/${id}/export`);
  return res.data;
}

export async function importWorkflow(yaml: string): Promise<Workflow> {
  const res = await client.post<Workflow>("/workflows/import", { yaml });
  return res.data;
}
