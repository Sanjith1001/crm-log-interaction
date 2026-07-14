import { StructuredInteractionForm } from "../components/form/StructuredInteractionForm";
import { ChatPanel } from "../components/chat/ChatPanel";
import "./pages.css";

export function LogInteractionPage() {
  return (
    <div className="log-page-container">
      <div className="log-content-grid">
        <StructuredInteractionForm />
        <ChatPanel />
      </div>
    </div>
  );
}
export default LogInteractionPage;
