import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider } from "./store/AuthContext";
import { AppLayout } from "./components/Layout/AppLayout";
import { RouteGuard, GuestGuard } from "./components/Layout/RouteGuard";
import { EditorPage } from "./pages/EditorPage";
import { WorkflowListPage } from "./pages/WorkflowListPage";
import { LoginPage } from "./pages/LoginPage";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes */}
        <Route element={<GuestGuard />}>
          <Route path="/login" element={<LoginPage />} />
        </Route>
        {/* Protected routes */}
        <Route element={<RouteGuard />}>
          <Route element={<AppLayout />}>
            <Route path="/workflows" element={<WorkflowListPage />} />
            <Route path="/editor/:workflowId" element={<EditorPage />} />
            <Route path="/editor/new" element={<EditorPage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </AuthProvider>
  );
}
