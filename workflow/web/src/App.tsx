import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./store/AuthContext";
import { AppLayout } from "./components/Layout/AppLayout";
import { RouteGuard, GuestGuard } from "./components/Layout/RouteGuard";
import { EditorPage } from "./pages/EditorPage";
import { WorkflowListPage } from "./pages/WorkflowListPage";
import { RunListPage } from "./pages/RunListPage";
import { RunDetailPage } from "./pages/RunDetailPage";
import { LoginPage } from "./pages/LoginPage";
import { TemplateMarketPage } from "./pages/TemplateMarketPage";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route element={<GuestGuard />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>
        <Route element={<RouteGuard />}>
          <Route element={<AppLayout />}>
            <Route path="/workflows" element={<WorkflowListPage />} />
            <Route path="/runs" element={<RunListPage />} />
            <Route path="/runs/:runId" element={<RunDetailPage />} />`n            <Route path="/templates" element={<TemplateMarketPage />} />
            <Route path="/editor/:workflowId" element={<EditorPage />} />
            <Route path="/editor/new" element={<EditorPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </AuthProvider>
  );
}
