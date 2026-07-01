import { useRef, useEffect, useState, useCallback } from "react";
import { Button, message } from "antd";
import { CopyOutlined } from "@ant-design/icons";

interface DslEditorProps {
  value: string;
  onChange: (value: string) => void;
  readOnly?: boolean;
  height?: string;
}

export function DslEditor({ value, onChange, readOnly = false, height = "100%" }: DslEditorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const editorRef = useRef<any>(null);
  const prevValueRef = useRef(value);
  const [copied, setCopied] = useState(false);

  // Load Monaco dynamically
  useEffect(() => {
    let editor: any = null;

    const init = async () => {
      try {
        const monaco = await import("monaco-editor");

        if (!containerRef.current) return;
        // Register YAML language
        monaco.languages.register({ id: "yaml" });

        editor = monaco.editor.create(containerRef.current, {
          value: value,
          language: "yaml",
          theme: "vs-dark",
          fontSize: 13,
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          lineNumbers: "on",
          minimap: { enabled: false },
          scrollBeyondLastLine: false,
          readOnly: readOnly,
          automaticLayout: true,
          tabSize: 2,
          wordWrap: "on",
          renderWhitespace: "selection",
          padding: { top: 12, bottom: 12 },
        });

        editor.onDidChangeModelContent(() => {
          const newValue = editor.getValue();
          if (newValue !== prevValueRef.current) {
            prevValueRef.current = newValue;
            onChange(newValue);
          }
        });

        editorRef.current = editor;
      } catch (err) {
        console.error("Failed to load Monaco Editor:", err);
      }
    };

    init();

    return () => {
      if (editor) editor.dispose();
    };
  }, []);

  // Update value from outside
  useEffect(() => {
    if (editorRef.current && value !== prevValueRef.current) {
      prevValueRef.current = value;
      editorRef.current.setValue(value);
    }
  }, [value]);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(true);
      message.success("Copied to clipboard");
      setTimeout(() => setCopied(false), 2000);
    });
  }, [value]);

  return (
    <div style={{ position: "relative", height, background: "#1E1E1E", borderRadius: 8, overflow: "hidden" }}>
      <div style={{ position: "absolute", top: 8, right: 8, zIndex: 10 }}>
        <Button
          size="small"
          icon={copied ? undefined : <CopyOutlined />}
          onClick={handleCopy}
          style={{ background: "rgba(255,255,255,0.1)", color: "#CBD5E1", border: "1px solid rgba(255,255,255,0.15)" }}
        >
          {copied ? "Copied" : "Copy"}
        </Button>
      </div>
      <div ref={containerRef} style={{ width: "100%", height: "100%" }} />
    </div>
  );
}
