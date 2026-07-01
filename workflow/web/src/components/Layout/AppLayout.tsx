import { TopNav } from "./TopNav";
import { Outlet } from "react-router-dom";

export function AppLayout() {
  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <TopNav />
      <div style={{ flex: 1, position: "relative", overflow: "hidden" }}>
        <div className="animate-page-enter" style={{ height: "100%" }}>
          <Outlet />
        </div>
      </div>
    </div>
  );
}
