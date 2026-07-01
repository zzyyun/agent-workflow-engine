import React from "react";
import { Button } from "antd";
import { ReloadOutlined } from "@ant-design/icons";

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("[ErrorBoundary]", error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div style={{
          display: "flex", flexDirection: "column",
          alignItems: "center", justifyContent: "center",
          height: "100%", padding: 40, gap: 16,
          background: "#F8FAFC",
        }}>
          <div style={{
            width: 64, height: 64, borderRadius: 16,
            background: "#FEF2F2", display: "flex",
            alignItems: "center", justifyContent: "center",
            fontSize: 28,
          }}>
            !
          </div>
          <h3 style={{ fontFamily: "'DM Sans', system-ui", fontSize: 16, color: "#0F172A", fontWeight: 600, margin: 0 }}>
            Something went wrong
          </h3>
          <p style={{ fontSize: 13, color: "#64748B", maxWidth: 400, textAlign: "center", lineHeight: 1.6, margin: 0 }}>
            An unexpected error occurred. Please try again or contact support if the problem persists.
          </p>
          {this.state.error && (
            <pre style={{
              fontFamily: "'JetBrains Mono', monospace", fontSize: 11, lineHeight: 1.5,
              background: "#FEF2F2", borderRadius: 8, padding: 12, overflow: "auto",
              maxWidth: 500, maxHeight: 120, color: "#991B1B", border: "1px solid #FECACA",
              whiteSpace: "pre-wrap", wordBreak: "break-all", margin: 0,
            }}>
              {this.state.error.message}
            </pre>
          )}
          <Button type="primary" icon={<ReloadOutlined />} onClick={this.handleRetry}>
            Try Again
          </Button>
        </div>
      );
    }

    return this.props.children;
  }
}
