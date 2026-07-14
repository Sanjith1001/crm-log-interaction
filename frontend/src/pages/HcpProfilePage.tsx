import { useState } from "react";
import { useGetHcpsQuery, useGetHcpByIdQuery } from "../store/api/agentApi";
import "./pages.css";

export function HcpProfilePage() {
  const [selectedHcpId, setSelectedHcpId] = useState<string | null>(null);
  const { data: hcps = [], isLoading } = useGetHcpsQuery();
  const [recommendation, setRecommendation] = useState("");
  const [isRecLoading, setIsRecLoading] = useState(false);

  const handleGetRecommendation = async (hcp: any) => {
    setIsRecLoading(true);
    setRecommendation("");
    
    try {
      const response = await fetch("/api/agent/invoke", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: `rec-${hcp.id}`,
          input_mode: "chat",
          raw_input: `Generate a follow-up recommendation for ${hcp.name}`,
        }),
      });

      if (!response.body) throw new Error("No body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.substring(6));
              if (data.event === "token") {
                setRecommendation((prev) => prev + data.token);
              }
            } catch (e) {
              console.error(e);
            }
          }
        }
      }
    } catch (err) {
      setRecommendation("Error retrieving recommendations.");
    } finally {
      setIsRecLoading(false);
    }
  };

  if (isLoading) {
    return <div style={{ padding: 40, textAlign: "center" }}>Loading HCP directory...</div>;
  }

  return (
    <div>
      {!selectedHcpId ? (
        <div className="hcp-grid">
          {hcps.map((hcp) => (
            <div key={hcp.id} className="hcp-card" onClick={() => setSelectedHcpId(hcp.id)}>
              <div className="hcp-header">
                <div className="hcp-name">{hcp.name}</div>
                <span className="hcp-specialty">{hcp.specialty}</span>
              </div>
              <div className="hcp-detail-item">
                <span>🏥</span> {hcp.hospital}
              </div>
              <div className="hcp-detail-item">
                <span>📍</span> {hcp.city}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <HcpDetailView
          hcpId={selectedHcpId}
          onBack={() => {
            setSelectedHcpId(null);
            setRecommendation("");
          }}
          recommendation={recommendation}
          isRecLoading={isRecLoading}
          onGetRecommendation={handleGetRecommendation}
        />
      )}
    </div>
  );
}

function HcpDetailView({
  hcpId,
  onBack,
  recommendation,
  isRecLoading,
  onGetRecommendation,
}: {
  hcpId: string;
  onBack: () => void;
  recommendation: string;
  isRecLoading: boolean;
  onGetRecommendation: (hcp: any) => void;
}) {
  const { data: hcpDetails, isLoading } = useGetHcpByIdQuery(hcpId);

  if (isLoading || !hcpDetails) {
    return <div style={{ padding: 40, textAlign: "center" }}>Loading profile details...</div>;
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
        <button className="logout-btn" onClick={onBack}>
          ← Back to Directory
        </button>
        <h2 style={{ fontSize: 22, fontWeight: 700 }}>{hcpDetails.name}</h2>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
        <div className="panel-card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Card Profile</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 12, fontSize: 14 }}>
            <div>
              <span style={{ color: "var(--text-secondary)" }}>Specialty: </span>
              <strong>{hcpDetails.specialty}</strong>
            </div>
            <div>
              <span style={{ color: "var(--text-secondary)" }}>Hospital: </span>
              <strong>{hcpDetails.hospital}</strong>
            </div>
            <div>
              <span style={{ color: "var(--text-secondary)" }}>Location: </span>
              <strong>{hcpDetails.city}</strong>
            </div>
            {hcpDetails.prescription_preferences && (
              <div style={{ marginTop: 8, borderTop: "1px solid var(--border)", paddingTop: 12 }}>
                <span style={{ color: "var(--text-secondary)", display: "block", marginBottom: 6 }}>
                  Prescription Preferences:
                </span>
                <pre
                  style={{
                    backgroundColor: "var(--bg-tertiary)",
                    padding: 12,
                    borderRadius: 6,
                    fontFamily: "monospace",
                    fontSize: 12,
                  }}
                >
                  {JSON.stringify(hcpDetails.prescription_preferences, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
          <div className="panel-card" style={{ padding: 24 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <h3 style={{ fontSize: 16, fontWeight: 600 }}>Sales Actions</h3>
              <button
                className="login-btn"
                style={{ marginTop: 0 }}
                onClick={() => onGetRecommendation(hcpDetails)}
                disabled={isRecLoading}
              >
                {isRecLoading ? "Analyzing..." : "✨ Get Follow-up Recommendation"}
              </button>
            </div>

            {(isRecLoading || recommendation) && (
              <div className="recommendation-box">
                <h4 className="recommendation-title">🤖 AI Strategy Recommendation</h4>
                <div
                  style={{
                    fontSize: 13,
                    lineHeight: 1.6,
                    whiteSpace: "pre-wrap",
                    color: "var(--text-primary)",
                  }}
                >
                  {recommendation || "Agent is analyzing interaction history..."}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="panel-card" style={{ padding: 24 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Recent Interactions Timeline</h3>
        {hcpDetails.recent_interactions?.length === 0 ? (
          <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>No logged visits recorded.</p>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {hcpDetails.recent_interactions.map((inter: any) => (
              <div
                key={inter.id}
                style={{
                  padding: 16,
                  backgroundColor: "var(--bg-tertiary)",
                  borderRadius: "var(--border-radius-sm)",
                  border: "1px solid var(--border)",
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <strong>Visit on {inter.visit_date}</strong>
                  <span className={`source-badge ${inter.source}`}>{inter.source}</span>
                </div>
                <p style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 8 }}>
                  {inter.summary}
                </p>
                {inter.products_discussed?.length > 0 && (
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                    Products discussed: {inter.products_discussed.join(", ")}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
export default HcpProfilePage;
