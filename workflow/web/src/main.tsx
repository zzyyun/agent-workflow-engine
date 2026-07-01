import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ConfigProvider } from "antd";
import App from "./App";
import "./styles/tokens.css";
import "./styles/animations.css";
import "./styles/nodes.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <ConfigProvider
        theme={{
          token: {
            colorPrimary: "#818CF8",
            colorBgLayout: "#F8FAFC",
            colorBorder: "#E2E8F0",
            colorText: "#0F172A",
            colorTextSecondary: "#64748B",
            borderRadius: 8,
            fontFamily: '"Inter", system-ui, sans-serif',
          },
        }}
      >
        <App />
      </ConfigProvider>
    </BrowserRouter>
  </StrictMode>
);
