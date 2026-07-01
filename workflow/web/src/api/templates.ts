import client from "./client";
import type { WorkflowTemplate } from "../types/workflow";

export interface TemplateListResponse {
  items: WorkflowTemplate[];
  total: number;
}

export async function listTemplates(params?: {
  category?: string;
  search?: string;
  page?: number;
  size?: number;
}): Promise<TemplateListResponse> {
  const res = await client.get("/templates", { params });
  return res.data;
}

export async function getTemplate(templateId: string): Promise<WorkflowTemplate> {
  const res = await client.get(`/templates/${templateId}`);
  return res.data;
}

export async function createFromTemplate(templateId: string, name?: string): Promise<{ id: string; name: string }> {
  const res = await client.post(`/templates/${templateId}/create`, { name });
  return res.data;
}
