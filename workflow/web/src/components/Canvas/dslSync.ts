import type { Node, Edge } from "@xyflow/react";
import { dump, load } from "js-yaml";

interface DslWorkflow {
  workflow: { name: string; description?: string };
  nodes: Array<{
    id: string;
    type: string;
    label: string;
    config?: Record<string, unknown>;
    position: { x: number; y: number };
  }>;
  edges: Array<{
    source: string;
    target: string;
    label?: string;
    expression?: string;
  }>;
}

export function serializeToObject(nodes: Node[], edges: Edge[]): Record<string, unknown> {
  const dsl: DslWorkflow = {
    workflow: { name: "Unnamed Workflow" },
    nodes: nodes.map(n => ({
      id: n.id,
      type: String(n.data?.nodeType ?? "llm"),
      label: String(n.data?.label ?? ""),
      config: n.data?.config as Record<string, unknown> | undefined,
      position: { x: Math.round(n.position.x), y: Math.round(n.position.y) },
    })),
    edges: edges.map(e => ({
      source: e.source,
      target: e.target,
      label: typeof e.label === "string" ? e.label : undefined,
      expression: e.data?.expression as string | undefined,
    })),
  };
  return dsl as unknown as Record<string, unknown>;
}

export function serializeToYaml(nodes: Node[], edges: Edge[]): string {
  const obj = serializeToObject(nodes, edges);
  return dump(obj, { indent: 2, lineWidth: -1, noRefs: true });
}

export function parseFromObject(json: Record<string, unknown>): { nodes: Partial<Node>[]; edges: Partial<Edge>[] } {
  const dsl = json as unknown as DslWorkflow;
  const nodes: Partial<Node>[] = (dsl.nodes || []).map(n => ({
    id: n.id,
    type: "canvasNode",
    position: n.position,
    data: {
      nodeType: n.type,
      label: n.label,
      description: `${n.type} node`,
      config: n.config || {},
      status: "pending",
    },
  }));
  const edges: Partial<Edge>[] = (dsl.edges || []).map(e => ({
    id: `e-${e.source}-${e.target}`,
    source: e.source,
    target: e.target,
    label: e.label,
    animated: true,
    style: { stroke: "rgba(129,140,248,0.5)", strokeWidth: 2.5 },
  }));
  const usedPositions = new Set<string>();
  nodes.forEach(n => {
    const key = `${n.position!.x},${n.position!.y}`;
    if (usedPositions.has(key)) {
      n.position!.x += 40 * (nodes.indexOf(n) + 1);
      n.position!.y += 40 * (nodes.indexOf(n) + 1);
    }
    usedPositions.add(`${n.position!.x},${n.position!.y}`);
  });
  return { nodes, edges };
}

export function parseFromYaml(dslYaml: string): { nodes: Partial<Node>[]; edges: Partial<Edge>[] } | null {
  try {
    const doc = load(dslYaml) as Record<string, unknown>;
    return parseFromObject(doc);
  } catch (err) {
    console.error("YAML parse error:", err);
    return null;
  }
}
