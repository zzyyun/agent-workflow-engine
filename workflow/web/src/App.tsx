import { Routes, Route, Navigate } from "react-router-dom";
import { AppLayout } from "./components/Layout/AppLayout";
import { EditorPage } from "./pages/EditorPage";
import { WorkflowListPage } from "./pages/WorkflowListPage";
import { LoginPage } from "./pages/LoginPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<AppLayout />}>
        <Route path="/workflows" element={<WorkflowListPage />} />
        <Route path="/editor/:workflowId" element={<EditorPage />} />
        <Route path="/editor/new" element={<EditorPage />} />
        <Route path="*" element={<Navigate to="/workflows" replace />} />
      </Route>
    </Routes>
  );
}
