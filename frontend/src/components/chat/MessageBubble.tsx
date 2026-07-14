import { useDispatch, useSelector } from "react-redux";
import { Message, setPendingConfirmation, addMessage } from "../../store/slices/chatSlice";
import { ToolCallBadge } from "./ToolCallBadge";
import { ExtractedEntitiesPanel } from "../interaction/ExtractedEntitiesPanel";
import { RootState } from "../../store/store";
import "../../pages/pages.css";

export function MessageBubble({ message }: { message: Message }) {
  const dispatch = useDispatch();
  const sessionId = useSelector((state: RootState) => state.chat.sessionId);
  const isUser = message.sender === "user";

  const handleConfirm = async (choice: "confirm" | "cancel") => {
    dispatch(setPendingConfirmation(null));
    
    dispatch(addMessage({
      id: `confirm-${Date.now()}-user`,
      sender: "user",
      text: choice === "confirm" ? "Confirm changes" : "Cancel changes"
    }));

    try {
      const response = await fetch("/api/agent/confirm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, choice }),
      });
      const data = await response.json();
      
      dispatch(addMessage({
        id: `confirm-${Date.now()}-agent`,
        sender: "agent",
        text: data.final_response,
        toolCalls: data.tool_calls_made
      }));
    } catch (e) {
      dispatch(addMessage({
        id: `confirm-${Date.now()}-agent`,
        sender: "agent",
        text: "Error executing confirmation."
      }));
    }
  };

  return (
    <div className={`message-bubble ${message.sender}`}>
      <span className="bubble-sender">{isUser ? "You" : "Agent"}</span>
      <div className="bubble-content">
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="tool-badge-container">
            {message.toolCalls.map((t, idx) => (
              <ToolCallBadge key={idx} tool={t.tool} args={t.args} />
            ))}
          </div>
        )}

        <div style={{ whiteSpace: "pre-wrap" }}>
          {message.text ? (
            renderMarkdown(message.text)
          ) : (
            <span style={{ color: "var(--text-muted)", fontStyle: "italic" }}>
              Agent is typing...
            </span>
          )}
        </div>

        {message.toolCalls?.map((t, idx) => {
          if (t.tool === "log_interaction" && t.args && Object.keys(t.args).length > 2) {
            return <ExtractedEntitiesPanel key={idx} entities={t.args} />;
          }
          return null;
        })}

        {message.pendingConfirmation && (
          <div style={{ marginTop: 12, borderTop: "1px solid var(--border)", paddingTop: 12 }}>
            <h4 style={{ fontSize: 13, color: "var(--warning)", marginBottom: 8 }}>
              ⚠️ Proposed Updates
            </h4>
            <div style={{ display: "flex", flexDirection: "column", gap: 6, fontSize: 12, marginBottom: 12 }}>
              {Object.entries(message.pendingConfirmation.diff || {}).map(([key, val]: [string, any]) => {
                const formatVal = (v: any) => {
                  if (v === null || v === undefined) return "None";
                  if (Array.isArray(v)) {
                    if (v.length === 0) return "None";
                    if (key === "samples_given") {
                      return v.map((item: any) => `${item.product_name} (Qty: ${item.qty})`).join(", ");
                    }
                    if (key === "action_items") {
                      return v.map((item: any) => `${item.description} (Due: ${item.due_date || "N/A"})`).join(", ");
                    }
                    return JSON.stringify(v);
                  }
                  if (typeof v === "object") return JSON.stringify(v);
                  return String(v);
                };

                return (
                  <div key={key}>
                    <strong style={{ textTransform: "capitalize" }}>{key.replace(/_/g, " ")}</strong>:{" "}
                    <span style={{ textDecoration: "line-through", color: "var(--error)", marginRight: 6 }}>
                      {formatVal(val.before)}
                    </span>{" "}
                    ➔{" "}
                    <span style={{ color: "var(--success)", marginLeft: 6 }}>
                      {formatVal(val.after)}
                    </span>
                  </div>
                );
              })}
            </div>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                onClick={() => handleConfirm("confirm")}
                style={{
                  backgroundColor: "var(--success)",
                  color: "white",
                  border: "none",
                  padding: "6px 12px",
                  borderRadius: 4,
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: "bold",
                }}
              >
                Confirm Save
              </button>
              <button
                onClick={() => handleConfirm("cancel")}
                style={{
                  backgroundColor: "var(--error)",
                  color: "white",
                  border: "none",
                  padding: "6px 12px",
                  borderRadius: 4,
                  cursor: "pointer",
                  fontSize: 12,
                  fontWeight: "bold",
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function renderMarkdown(text: string) {
  const lines = text.split("\n");
  return lines.map((line, index) => {
    let content = line;
    if (content.startsWith("### ")) {
      return <h4 key={index} style={{ margin: "8px 0", fontSize: "14px", fontWeight: "bold", color: "var(--accent-ai)" }}>{parseInlineMarkdown(content.substring(4))}</h4>;
    }
    if (content.startsWith("## ")) {
      return <h3 key={index} style={{ margin: "10px 0", fontSize: "16px", fontWeight: "bold", color: "var(--accent-ai)" }}>{parseInlineMarkdown(content.substring(3))}</h3>;
    }
    if (content.startsWith("# ")) {
      return <h2 key={index} style={{ margin: "12px 0", fontSize: "18px", fontWeight: "bold", color: "var(--accent-ai)" }}>{parseInlineMarkdown(content.substring(2))}</h2>;
    }
    if (content.startsWith("* ") || content.startsWith("- ")) {
      return <li key={index} style={{ marginLeft: "16px", marginBottom: "4px", listStyleType: "disc" }}>{parseInlineMarkdown(content.substring(2))}</li>;
    }
    if (content.trim() === "") {
      return <div key={index} style={{ height: "8px" }} />;
    }
    return <p key={index} style={{ margin: "4px 0", lineHeight: "1.5" }}>{parseInlineMarkdown(content)}</p>;
  });
}

function parseInlineMarkdown(text: string) {
  const regex = /(\*\*.*?\*\*|`.*?`)/g;
  const matches = text.split(regex);
  return matches.map((part, idx) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={idx}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={idx} style={{ backgroundColor: "rgba(255,255,255,0.15)", padding: "2px 4px", borderRadius: "3px", fontFamily: "monospace" }}>{part.slice(1, -1)}</code>;
    }
    return part;
  });
}

