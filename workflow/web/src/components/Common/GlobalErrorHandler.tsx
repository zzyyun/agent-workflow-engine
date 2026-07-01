import { useEffect } from "react";
import { message } from "antd";

export function GlobalErrorHandler() {
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      console.error("[Global] Uncaught error:", event.error || event.message);
      message.error({
        content: "An unexpected error occurred",
        key: "global-error",
        duration: 4,
      });
    };

    const handleRejection = (event: PromiseRejectionEvent) => {
      console.error("[Global] Unhandled rejection:", event.reason);
      const msg = event.reason?.message || event.reason || "Promise rejected";
      message.error({
        content: msg.length > 80 ? msg.slice(0, 80) + "..." : msg,
        key: "global-rejection",
        duration: 4,
      });
    };

    window.addEventListener("error", handleError);
    window.addEventListener("unhandledrejection", handleRejection);

    return () => {
      window.removeEventListener("error", handleError);
      window.removeEventListener("unhandledrejection", handleRejection);
    };
  }, []);

  return null;
}
