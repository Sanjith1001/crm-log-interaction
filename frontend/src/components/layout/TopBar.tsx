import { useDispatch, useSelector } from "react-redux";
import { RootState } from "../../store/store";
import { setCurrentPage } from "../../store/slices/uiSlice";
import { clearChat } from "../../store/slices/chatSlice";
import "./layout.css";

export function TopBar() {
  const dispatch = useDispatch();
  const currentPage = useSelector((state: RootState) => state.ui.currentPage);

  if (currentPage === "login") return null;

  const getPageTitle = () => {
    switch (currentPage) {
      case "log":
        return "Log HCP Interaction";
      case "history":
        return "Interaction History";
      case "hcp":
        return "Healthcare Professional Directory";
      default:
        return "Aegis CRM";
    }
  };

  const handleLogout = () => {
    dispatch(clearChat());
    dispatch(setCurrentPage("login"));
  };

  return (
    <header className="topbar">
      <h1 className="page-title">{getPageTitle()}</h1>
      <div className="user-profile">
        <span className="rep-badge">Demo Rep (Territory: South)</span>
      </div>
    </header>
  );
}
