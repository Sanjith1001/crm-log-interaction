import { useState } from "react";
import { useDispatch } from "react-redux";
import { useGetInteractionsQuery } from "../store/api/agentApi";
import { setCurrentPage, setActiveMode } from "../store/slices/uiSlice";
import { addMessage } from "../store/slices/chatSlice";
import "./pages.css";

export function InteractionHistoryPage() {
  const dispatch = useDispatch();
  const [search, setSearch] = useState("");
  const { data: interactions = [], isLoading, refetch } = useGetInteractionsQuery({ query: search });
  const [selectedItem, setSelectedItem] = useState<any | null>(null);

  const handleAskAi = () => {
    dispatch(addMessage({
      id: `ask-ai-${Date.now()}`,
      sender: "user",
      text: `Show me all interactions matching "${search}"`
    }));
    dispatch(setCurrentPage("log"));
    dispatch(setActiveMode("chat"));
  };

  const handleEditClick = (item: any) => {
    dispatch(addMessage({
      id: `edit-prompt-${Date.now()}`,
      sender: "user",
      text: `Edit the interaction with ${item.hcp_name} on ${item.visit_date}: `
    }));
    dispatch(setCurrentPage("log"));
    dispatch(setActiveMode("chat"));
  };

  return (
    <div className="history-container">
      <div className="filter-bar">
        <div className="filter-inputs">
          <input
            type="text"
            className="form-input"
            style={{ flexGrow: 1 }}
            placeholder="Search doctor name, hospital, category..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button className="login-btn" style={{ marginTop: 0 }} onClick={() => refetch()}>
            Search
          </button>
        </div>
        {search.trim() && (
          <button
            onClick={handleAskAi}
            style={{
              background: "none",
              border: "1px solid var(--accent-ai)",
              color: "#c084fc",
              padding: "10px 16px",
              borderRadius: "var(--border-radius-sm)",
              fontSize: 13,
              fontWeight: 600,
              cursor: "pointer",
            }}
          >
            ✨ Ask AI Instead
          </button>
        )}
      </div>

      <div className="history-card">
        {isLoading ? (
          <div style={{ padding: 40, textAlign: "center", color: "var(--text-secondary)" }}>
            Loading interactions history...
          </div>
        ) : interactions.length === 0 ? (
          <div style={{ padding: 40, textAlign: "center", color: "var(--text-secondary)" }}>
            No interactions found.
          </div>
        ) : (
          <table className="history-table">
            <thead>
              <tr>
                <th>Doctor</th>
                <th>Hospital</th>
                <th>Visit Date</th>
                <th>Products discussed</th>
                <th>Source</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {interactions.map((item) => (
                <tr key={item.id}>
                  <td>
                    <strong>{item.hcp_name}</strong>
                  </td>
                  <td>{item.hcp_hospital}</td>
                  <td>{item.visit_date}</td>
                  <td>{item.products_discussed.join(", ")}</td>
                  <td>
                    <span className={`source-badge ${item.source}`}>
                      {item.source}
                    </span>
                  </td>
                  <td>
                    <button
                      onClick={() => setSelectedItem(item)}
                      style={{
                        background: "none",
                        border: "none",
                        color: "var(--primary)",
                        cursor: "pointer",
                        fontWeight: 600,
                        marginRight: 12
                      }}
                    >
                      View Details
                    </button>
                    <button
                      onClick={() => handleEditClick(item)}
                      style={{
                        background: "none",
                        border: "none",
                        color: "var(--accent-ai)",
                        cursor: "pointer",
                        fontWeight: 600
                      }}
                    >
                      Edit via AI
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {selectedItem && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0, 0, 0, 0.7)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
          onClick={() => setSelectedItem(null)}
        >
          <div
            className="panel-card"
            style={{ width: "90%", maxWidth: 640, height: "fit-content", padding: 24 }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
              <h3 style={{ fontSize: 18, fontWeight: 700 }}>Visit Details</h3>
              <button
                style={{ background: "none", border: "none", fontSize: 18, color: "var(--text-secondary)", cursor: "pointer" }}
                onClick={() => setSelectedItem(null)}
              >
                ✕
              </button>
            </div>
            
            <div style={{ display: "flex", flexDirection: "column", gap: 16, fontSize: 14 }}>
              <div>
                <span style={{ color: "var(--text-secondary)" }}>Doctor: </span>
                <strong>{selectedItem.hcp_name} ({selectedItem.hcp_specialty})</strong>
              </div>
              <div>
                <span style={{ color: "var(--text-secondary)" }}>Hospital: </span>
                <strong>{selectedItem.hcp_hospital}</strong>
              </div>
              <div>
                <span style={{ color: "var(--text-secondary)" }}>Visit Date: </span>
                <strong>{selectedItem.visit_date}</strong>
              </div>
              <div>
                <span style={{ color: "var(--text-secondary)" }}>AI Summary: </span>
                <p style={{ marginTop: 6, padding: 12, backgroundColor: "var(--bg-tertiary)", borderRadius: 6, border: "1px solid var(--border)" }}>
                  {selectedItem.summary}
                </p>
              </div>
              {selectedItem.samples_given && selectedItem.samples_given.length > 0 && (
                <div>
                  <span style={{ color: "var(--text-secondary)" }}>Samples Distributed: </span>
                  <ul>
                    {selectedItem.samples_given.map((s: any, idx: number) => (
                      <li key={idx}>• {s.product_name} (Qty: {s.qty})</li>
                    ))}
                  </ul>
                </div>
              )}
              {selectedItem.action_items && selectedItem.action_items.length > 0 && (
                <div>
                  <span style={{ color: "var(--text-secondary)" }}>Action Items: </span>
                  <ul>
                    {selectedItem.action_items.map((a: any, idx: number) => (
                      <li key={idx}>• {a.description} {a.due_date && `(Due: ${a.due_date})`}</li>
                    ))}
                  </ul>
                </div>
              )}
              {selectedItem.follow_up_date && (
                <div>
                  <span style={{ color: "var(--text-secondary)" }}>Proposed Follow-up Date: </span>
                  <strong>{selectedItem.follow_up_date}</strong>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
export default InteractionHistoryPage;
