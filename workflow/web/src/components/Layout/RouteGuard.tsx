import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../../store/AuthContext";

export function RouteGuard() {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function GuestGuard() {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) return <Navigate to="/workflows" replace />;
  return <Outlet />;
}
