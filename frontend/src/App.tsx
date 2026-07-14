import { useSelector } from "react-redux";
import { RootState } from "./store/store";
import { AppShell } from "./components/layout/AppShell";
import { LogInteractionPage } from "./pages/LogInteractionPage";
import { InteractionHistoryPage } from "./pages/InteractionHistoryPage";
import { HcpProfilePage } from "./pages/HcpProfilePage";
import { LoginPage } from "./pages/LoginPage";

export default function App() {
  const currentPage = useSelector((state: RootState) => state.ui.currentPage);

  const renderPage = () => {
    switch (currentPage) {
      case "login":
        return <LoginPage />;
      case "log":
        return <LogInteractionPage />;
      case "history":
        return <InteractionHistoryPage />;
      case "hcp":
        return <HcpProfilePage />;
      default:
        return <LoginPage />;
    }
  };

  return (
    <AppShell>
      {renderPage()}
    </AppShell>
  );
}
