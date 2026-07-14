import { useState } from "react";
import "../../pages/pages.css";

interface ToolCallBadgeProps {
  tool: string;
  args: any;
}

export function ToolCallBadge({ tool, args }: ToolCallBadgeProps) {
  const [showPanel, setShowPanel] = useState(false);

  const getToolLabel = (name: string) => {
    switch (name) {
      case "log_interaction":
        return "Log Interaction";
      case "edit_interaction":
        return "Edit Interaction";
      case "search_interaction":
        return "Search History";
      case "hcp_lookup":
        return "HCP Lookup";
      case "followup_recommendation":
        return "Get Recommendation";
      default:
        return name;
    }
  };

  return (
    <div style={{ position: "relative" }}>
      <button className="tool-badge" onClick={() => setShowPanel(!showPanel)}>
        <span>🛠</span>
        Agent called: {getToolLabel(tool)}
      </button>

      {showPanel && (
        <div className="entities-panel">
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6, fontWeight: "bold" }}>
            <span>Payload Arguments</span>
            <button
              style={{ background: "none", border: "none", color: "var(--text-muted)", cursor: "pointer" }}
              onClick={() => setShowPanel(false)}
            >
              ✕
            </button>
          </div>
          <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(args, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
