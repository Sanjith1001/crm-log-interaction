import { ReactNode } from "react";
import { useSelector } from "react-redux";
import { RootState } from "../../store/store";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import "./layout.css";

export function AppShell({ children }: { children: ReactNode }) {
  const currentPage = useSelector((state: RootState) => state.ui.currentPage);

  if (currentPage === "login") {
    return <>{children}</>;
  }

  return (
    <div className="app-container">
      <Sidebar />
      <div style={{ flexGrow: 1 }}>
        <TopBar />
        <main className="main-content">{children}</main>
      </div>
    </div>
  );
}
