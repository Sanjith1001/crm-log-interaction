import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store/store";
import { setCurrentPage, PageView } from "../../store/slices/uiSlice";
import "./layout.css";

export function Sidebar() {
  const dispatch = useDispatch();
  const currentPage = useSelector((state: RootState) => state.ui.currentPage);

  const navItems: Array<{ id: PageView; label: string; icon: string }> = [
    { id: "log", label: "Log Interaction", icon: "📝" },
    { id: "history", label: "Interaction History", icon: "📊" },
    { id: "hcp", label: "HCP Directory", icon: "👨‍⚕️" },
  ];

  if (currentPage === "login") return null;

  return (
    <aside className="sidebar">
      <div className="logo-container">
        <div className="logo-text">
          <div className="logo-icon" />
          Aegis CRM
        </div>
      </div>
      <nav className="nav-links">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-link ${currentPage === item.id ? "active" : ""}`}
            onClick={() => dispatch(setCurrentPage(item.id))}
          >
            <span>{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>
      <div className="sidebar-footer">
        <p>Aegis AI v1.0.0</p>
      </div>
    </aside>
  );
}
