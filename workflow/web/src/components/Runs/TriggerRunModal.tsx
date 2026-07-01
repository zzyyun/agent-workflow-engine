import { useState, useEffect, useCallback } from "react";
import { Modal, Select, Input, Form, message, Spin, Empty } from "antd";
import { ThunderboltOutlined } from "@ant-design/icons";
import { triggerRun } from "../../api/runs";
import { listWorkflows, type Workflow } from "../../api/workflows";

interface TriggerRunModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: (runId: string) => void;
  preselectedWorkflowId?: string;
}

export function TriggerRunModal({ open, onClose, onSuccess, preselectedWorkflowId }: TriggerRunModalProps) {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [selectedWf, setSelectedWf] = useState<string | undefined>(preselectedWorkflowId);
  const [inputParams, setInputParams] = useState("{}");
  const [form] = Form.useForm();

  const loadWorkflows = useCallback(async () => {
    setLoading(true);
    try {
      const res = await listWorkflows({ page: 1, size: 200 });
      setWorkflows(res.items || []);
    } catch {
      message.error("Failed to load workflows");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (open) {
      loadWorkflows();
      setSelectedWf(preselectedWorkflowId);
      setInputParams("{}");
      form.resetFields();
    }
  }, [open, preselectedWorkflowId, loadWorkflows, form]);

  const handleTrigger = async () => {
    if (!selectedWf) {
      message.warning("Please select a workflow");
      return;
    }
    setSubmitting(true);
    try {
      let parsedInput: Record<string, unknown> | undefined;
      if (inputParams.trim()) {
        try {
          parsedInput = JSON.parse(inputParams);
        } catch {
          message.error("Invalid JSON input parameters");
          setSubmitting(false);
          return;
        }
      }
      const result = await triggerRun(selectedWf, parsedInput);
      message.success("Task triggered successfully");
      onSuccess(result.runId);
      onClose();
    } catch {
      message.error("Failed to trigger task");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      title={
        <span style={{ fontFamily: "var(--font-display)", fontWeight: 600, fontSize: 15 }}>
          <ThunderboltOutlined style={{ marginRight: 8, color: "var(--primary)" }} />
          Trigger Workflow Run
        </span>
      }
      open={open}
      onCancel={onClose}
      onOk={handleTrigger}
      okText="Trigger Run"
      okButtonProps={{
        loading: submitting,
        disabled: !selectedWf,
        icon: <ThunderboltOutlined />,
        style: { boxShadow: "var(--primary-glow)" },
      }}
      cancelText="Cancel"
      width={480}
      destroyOnClose
      centered
    >
      {loading ? (
        <div style={{ textAlign: "center", padding: 40 }}><Spin /></div>
      ) : workflows.length === 0 ? (
        <Empty description="No workflows available. Create one first." />
      ) : (
        <Form form={form} layout="vertical" style={{ marginTop: 8 }}>
          <Form.Item label="Workflow" required>
            <Select
              placeholder="Select a workflow to run"
              value={selectedWf}
              onChange={setSelectedWf}
              showSearch
              optionFilterProp="label"
              options={workflows.map(w => ({
                label: w.name,
                value: w.id,
              }))}
              style={{ width: "100%" }}
              size="middle"
            />
          </Form.Item>
          <Form.Item
            label={
              <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
                Input Parameters <span style={{ color: "var(--text-muted)" }}>(JSON, optional)</span>
              </span>
            }
          >
            <Input.TextArea
              value={inputParams}
              onChange={e => setInputParams(e.target.value)}
              rows={6}
              placeholder='{"key": "value"}'
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 12,
                background: "#F8FAFC",
                borderRadius: 6,
              }}
            />
          </Form.Item>
          {selectedWf && (
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: -8 }}>
              Running: <strong>{workflows.find(w => w.id === selectedWf)?.name}</strong>
            </div>
          )}
        </Form>
      )}
    </Modal>
  );
}
