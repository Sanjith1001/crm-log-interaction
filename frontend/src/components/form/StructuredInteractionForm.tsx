import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { RootState } from "../../store/store";
import { useGetHcpsQuery } from "../../store/api/agentApi";
import { useAgentStream } from "../../hooks/useAgentStream";
import "../../pages/pages.css";

export function StructuredInteractionForm() {
  const { data: hcps = [] } = useGetHcpsQuery();
  const { sendMessage, isStreaming } = useAgentStream();
  const messages = useSelector((state: RootState) => state.chat.messages);
  const pendingConfirmation = useSelector((state: RootState) => state.chat.pendingConfirmation);

  const [selectedHcpId, setSelectedHcpId] = useState("");
  const [interactionType, setInteractionType] = useState("Meeting");
  const [visitDate, setVisitDate] = useState(new Date().toISOString().split("T")[0]);
  const [visitTime, setVisitTime] = useState("19:30");
  const [attendees, setAttendees] = useState("");
  const [topics, setTopics] = useState("");
  const [productsDiscussed, setProductsDiscussed] = useState<string[]>([]);
  const [samples, setSamples] = useState<Array<{ product_name: string; qty: number }>>([]);
  const [actionItems, setActionItems] = useState<Array<{ description: string; due_date: string }>>([]);
  const [followUpDate, setFollowUpDate] = useState("");
  
  // Custom video-specified fields
  const [materialsShared, setMaterialsShared] = useState<string[]>([]);
  const [newMaterial, setNewMaterial] = useState("");
  const [sentiment, setSentiment] = useState("Positive");
  const [outcomes, setOutcomes] = useState("");

  // Voice note simulation state
  const [recordingState, setRecordingState] = useState<"idle" | "recording" | "done">("idle");

  // AI assistant form auto-fill synchronization hook
  useEffect(() => {
    console.log("StructuredForm Sync Triggered:", { pendingConfirmation, messages });

    // 1. Prioritize pending confirmation updates if they exist (live diff preview)
    if (pendingConfirmation && pendingConfirmation.args && pendingConfirmation.args.data) {
      const data = pendingConfirmation.args.data;
      console.log("StructuredForm Sync - Pending Confirmation:", data);
      
      if (data.hcp_id) {
        setSelectedHcpId(data.hcp_id);
      } else if (data.hcp_name && hcps.length > 0) {
        const match = hcps.find(h => h.name.toLowerCase().includes(data.hcp_name.toLowerCase()));
        if (match) setSelectedHcpId(match.id);
      }
      if (data.visit_date) {
        setVisitDate(data.visit_date);
      }
      if (data.raw_notes) {
        setTopics(data.raw_notes);
      }
      if (data.products) {
        const productIds = data.products.map((pName: string) => {
          if (pName.toLowerCase().includes("ozempic")) return "d0e6d45e-4c07-4228-b9a5-1ffef76e330e";
          if (pName.toLowerCase().includes("keytruda")) return "f0a6d45e-4c07-4228-b9a5-1ffef76e330f";
          if (pName.toLowerCase().includes("januvia")) return "a0a6d45e-4c07-4228-b9a5-1ffef76e3310";
          if (pName.toLowerCase().includes("lipitor")) return "b0a6d45e-4c07-4228-b9a5-1ffef76e3311";
          return pName;
        });
        setProductsDiscussed(productIds);
      }
      if (data.products_discussed) {
        setProductsDiscussed(data.products_discussed);
      }
      if (data.samples_given) {
        setSamples(data.samples_given);
      }
      if (data.action_items) {
        setActionItems(data.action_items);
      }
      if (data.follow_up_date) {
        setFollowUpDate(data.follow_up_date);
      }

      // Merge custom entities
      const ext = data.extracted_entities || {};
      if (ext.sentiment) {
        setSentiment(ext.sentiment);
      } else if (data.sentiment) {
        setSentiment(data.sentiment);
      }
      
      if (ext.materials_shared) {
        setMaterialsShared(ext.materials_shared);
      } else if (data.materials_shared) {
        setMaterialsShared(data.materials_shared);
      }
      
      if (ext.outcomes) {
        setOutcomes(ext.outcomes);
      } else if (data.outcomes) {
        setOutcomes(data.outcomes);
      }
      return;
    }

    // 2. Otherwise, sync only if the last message in the chat history contains a tool call
    const lastMsg = messages[messages.length - 1];
    if (lastMsg && lastMsg.toolCalls) {
      const toolCall = lastMsg.toolCalls.find(t => t.tool === "log_interaction" || t.tool === "edit_interaction");
      if (toolCall && toolCall.args) {
        const data = toolCall.args;
        
        // Handle Form Data wrapper if present
        const payload = data.data || data.form_data || data;
        
        if (payload.hcp_id) {
          setSelectedHcpId(payload.hcp_id);
        } else if (payload.hcp_name && hcps.length > 0) {
          const match = hcps.find(h => h.name.toLowerCase().includes(payload.hcp_name.toLowerCase()));
          if (match) setSelectedHcpId(match.id);
        }
        
        if (payload.visit_date) {
          setVisitDate(payload.visit_date);
        }
        if (payload.visit_time) {
          setVisitTime(payload.visit_time);
        }
        if (payload.attendees) {
          setAttendees(payload.attendees);
        }
        if (payload.interaction_type) {
          setInteractionType(payload.interaction_type);
        }
        
        if (payload.notes || payload.raw_notes) {
          setTopics(payload.notes || payload.raw_notes);
        }
        
        if (payload.products_discussed) {
          setProductsDiscussed(payload.products_discussed);
        }
        
        if (payload.samples_given) {
          setSamples(payload.samples_given);
        }
        
        if (payload.action_items) {
          setActionItems(payload.action_items);
        }
        
        if (payload.follow_up_date) {
          setFollowUpDate(payload.follow_up_date);
        }

        // Custom entities
        const ext = payload.extracted_entities || {};
        if (ext.sentiment) {
          setSentiment(ext.sentiment);
        } else if (payload.sentiment) {
          setSentiment(payload.sentiment);
        }
        
        if (ext.materials_shared) {
          setMaterialsShared(ext.materials_shared);
        } else if (payload.materials_shared) {
          setMaterialsShared(payload.materials_shared);
        }
        
        if (ext.outcomes) {
          setOutcomes(ext.outcomes);
        } else if (payload.outcomes) {
          setOutcomes(payload.outcomes);
        }
      }
    }
  }, [messages, pendingConfirmation, hcps]);

  const handleSimulateVoiceNote = () => {
    setRecordingState("recording");
    setTimeout(() => {
      setRecordingState("done");
      setTopics(
        "Met with Dr. Rao to discuss Lipitor efficacy and positive patient outcomes. " +
        "Distributed 5 samples of Lipitor. Doctor showed positive interest. Scheduled a follow-up in two weeks."
      );
      // Autofill corresponding items
      if (hcps.length > 0) {
        // Prefill Dr. Rao if exists
        const rao = hcps.find(h => h.name.toLowerCase().includes("rao"));
        if (rao) setSelectedHcpId(rao.id);
      }
      setProductsDiscussed(["b0a6d45e-4c07-4228-b9a5-1ffef76e3311"]); // Lipitor ID
      setSamples([{ product_name: "Lipitor", qty: 5 }]);
    }, 2000);
  };

  const handleAddSample = () => {
    setSamples([...samples, { product_name: "Ozempic", qty: 1 }]);
  };

  const handleRemoveSample = (idx: number) => {
    setSamples(samples.filter((_, i) => i !== idx));
  };

  const handleSampleChange = (idx: number, field: string, val: any) => {
    const updated = [...samples];
    updated[idx] = { ...updated[idx], [field]: val };
    setSamples(updated);
  };

  const handleAddActionItem = () => {
    setActionItems([...actionItems, { description: "", due_date: "" }]);
  };

  const handleRemoveActionItem = (idx: number) => {
    setActionItems(actionItems.filter((_, i) => i !== idx));
  };

  const handleActionItemChange = (idx: number, field: string, val: any) => {
    const updated = [...actionItems];
    updated[idx] = { ...updated[idx], [field]: val };
    setActionItems(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedHcpId || isStreaming) return;

    const selectedHcp = hcps.find((h) => h.id === selectedHcpId);

    const payload = {
      hcp_id: selectedHcpId,
      hcp_name: selectedHcp ? selectedHcp.name : "",
      interaction_type: interactionType,
      visit_date: visitDate,
      visit_time: visitTime,
      attendees: attendees,
      notes: topics,
      products_discussed: productsDiscussed,
      samples_given: samples,
      action_items: actionItems,
      follow_up_date: followUpDate || null,
      sentiment: sentiment,
      materials_shared: materialsShared,
      outcomes: outcomes,
      source: "form"
    };

    sendMessage(JSON.stringify(payload), "form");
  };

  const handleAddMaterial = () => {
    if (newMaterial.trim()) {
      setMaterialsShared([...materialsShared, newMaterial.trim()]);
      setNewMaterial("");
    }
  };

  const handleRemoveMaterial = (idx: number) => {
    setMaterialsShared(materialsShared.filter((_, i) => i !== idx));
  };

  return (
    <form className="panel-card" style={{ height: "100%", overflowY: "scroll", display: "block", padding: 24 }} onSubmit={handleSubmit}>
      <div className="panel-header" style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 20, fontWeight: 700 }}>Log HCP Interaction</h2>
        <span style={{ fontSize: 12, color: "var(--text-secondary)" }}>
          Interaction Details
        </span>
      </div>

      <div className="form-body" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {/* HCP Name & Interaction Type Row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="form-group">
            <label className="form-label">HCP Name</label>
            <select
              className="form-input"
              style={{ width: "100%" }}
              value={selectedHcpId}
              onChange={(e) => setSelectedHcpId(e.target.value)}
              required
            >
              <option value="">Search or select HCP...</option>
              {hcps.map((h) => (
                <option key={h.id} value={h.id}>
                  {h.name} - {h.specialty} ({h.hospital})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Interaction Type</label>
            <select
              className="form-input"
              style={{ width: "100%" }}
              value={interactionType}
              onChange={(e) => setInteractionType(e.target.value)}
            >
              <option value="Meeting">Meeting</option>
              <option value="Call">Call</option>
              <option value="Email">Email</option>
              <option value="Event">Event</option>
            </select>
          </div>
        </div>

        {/* Date & Time Row */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          <div className="form-group">
            <label className="form-label">Date</label>
            <input
              type="date"
              className="form-input"
              style={{ width: "100%" }}
              value={visitDate}
              onChange={(e) => setVisitDate(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Time</label>
            <input
              type="time"
              className="form-input"
              style={{ width: "100%" }}
              value={visitTime}
              onChange={(e) => setVisitTime(e.target.value)}
            />
          </div>
        </div>

        {/* Attendees */}
        <div className="form-group">
          <label className="form-label">Attendees</label>
          <input
            type="text"
            className="form-input"
            style={{ width: "100%" }}
            placeholder="Enter names or search..."
            value={attendees}
            onChange={(e) => setAttendees(e.target.value)}
          />
        </div>

        {/* Topics Discussed & Audio Transcription */}
        <div className="form-group">
          <label className="form-label">Topics Discussed</label>
          <textarea
            className="form-input"
            style={{ width: "100%" }}
            rows={4}
            value={topics}
            onChange={(e) => setTopics(e.target.value)}
            required
            placeholder="Enter key discussion points..."
          />
          <div style={{ marginTop: 6 }}>
            <button
              type="button"
              onClick={handleSimulateVoiceNote}
              style={{
                background: "none",
                border: "none",
                color: recordingState === "recording" ? "var(--error)" : "var(--primary)",
                fontSize: 12,
                cursor: "pointer",
                fontWeight: "bold",
                display: "flex",
                alignItems: "center",
                gap: 4
              }}
            >
              🎙️ {recordingState === "idle" && "Summarize from Voice Note (Requires Consent)"}
              {recordingState === "recording" && "Transcribing voice note... Please wait..."}
              {recordingState === "done" && "Transcribed! (Click to re-record)"}
            </button>
          </div>
        </div>

        {/* Products Discussed */}
        <div className="form-group">
          <label className="form-label">Products Discussed</label>
          <select
            multiple
            className="form-input"
            style={{ width: "100%", height: 130, padding: 8 }}
            value={productsDiscussed}
            onChange={(e) => {
              const options = Array.from(e.target.selectedOptions, (opt) => opt.value);
              setProductsDiscussed(options);
            }}
          >
            <option style={{ padding: "8px 12px", fontSize: "14px", borderRadius: 4, marginBottom: 4 }} value="d0e6d45e-4c07-4228-b9a5-1ffef76e330e">Ozempic</option>
            <option style={{ padding: "8px 12px", fontSize: "14px", borderRadius: 4, marginBottom: 4 }} value="f0a6d45e-4c07-4228-b9a5-1ffef76e330f">Keytruda</option>
            <option style={{ padding: "8px 12px", fontSize: "14px", borderRadius: 4, marginBottom: 4 }} value="a0a6d45e-4c07-4228-b9a5-1ffef76e3310">Januvia</option>
            <option style={{ padding: "8px 12px", fontSize: "14px", borderRadius: 4, marginBottom: 4 }} value="b0a6d45e-4c07-4228-b9a5-1ffef76e3311">Lipitor</option>
          </select>
        </div>

        {/* Materials Shared & Samples Distributed Section */}
        <div className="form-group" style={{ borderTop: "1px solid var(--border)", paddingTop: 16 }}>
          <span style={{ fontSize: 14, fontWeight: "bold", color: "var(--text-primary)", display: "block", marginBottom: 12 }}>
            Materials Shared / Samples Distributed
          </span>

          {/* Materials Shared sub-section */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <span style={{ fontSize: 13, fontWeight: "600", color: "var(--text-secondary)" }}>Materials Shared</span>
              <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                <input
                  type="text"
                  placeholder="e.g. Brochures."
                  className="form-input"
                  style={{ width: 140, padding: "4px 8px", fontSize: 12 }}
                  value={newMaterial}
                  onChange={(e) => setNewMaterial(e.target.value)}
                  onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); handleAddMaterial(); } }}
                />
                <button
                  type="button"
                  onClick={handleAddMaterial}
                  style={{
                    background: "var(--bg-secondary)",
                    border: "1px solid var(--border)",
                    color: "var(--text-primary)",
                    padding: "4px 8px",
                    borderRadius: 4,
                    fontSize: 12,
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: 4
                  }}
                >
                  🔍 Search/Add
                </button>
              </div>
            </div>

            {materialsShared.length === 0 ? (
              <span style={{ fontSize: 13, color: "var(--text-muted)", fontStyle: "italic" }}>No materials added.</span>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {materialsShared.map((mat, idx) => (
                  <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "6px 12px", background: "var(--bg-primary)", borderRadius: 4, border: "1px solid var(--border)" }}>
                    <span style={{ fontSize: 13, color: "var(--text-primary)" }}>{mat}</span>
                    <button
                      type="button"
                      onClick={() => handleRemoveMaterial(idx)}
                      style={{ background: "none", border: "none", color: "var(--error)", cursor: "pointer", fontSize: 12 }}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Samples Distributed sub-section */}
          <div style={{ marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
              <span style={{ fontSize: 13, fontWeight: "600", color: "var(--text-secondary)" }}>Samples Distributed</span>
              <button
                type="button"
                onClick={handleAddSample}
                style={{
                  background: "none",
                  border: "none",
                  color: "var(--primary)",
                  fontSize: 12,
                  cursor: "pointer",
                  fontWeight: "bold"
                }}
              >
                + Add Sample
              </button>
            </div>

            {samples.length === 0 ? (
              <span style={{ fontSize: 13, color: "var(--text-muted)", fontStyle: "italic" }}>No samples added.</span>
            ) : (
              samples.map((sample, idx) => (
                <div key={idx} style={{ display: "flex", gap: 12, marginBottom: 8 }}>
                  <select
                    className="form-input"
                    style={{ flexGrow: 1 }}
                    value={sample.product_name}
                    onChange={(e) => handleSampleChange(idx, "product_name", e.target.value)}
                  >
                    <option value="Ozempic">Ozempic</option>
                    <option value="Keytruda">Keytruda</option>
                    <option value="Januvia">Januvia</option>
                    <option value="Lipitor">Lipitor</option>
                  </select>
                  <input
                    type="number"
                    className="form-input"
                    style={{ width: 80 }}
                    value={sample.qty}
                    min={1}
                    onChange={(e) => handleSampleChange(idx, "qty", parseInt(e.target.value) || 1)}
                  />
                  <button
                    type="button"
                    onClick={() => handleRemoveSample(idx)}
                    style={{ background: "none", border: "none", color: "var(--error)", cursor: "pointer" }}
                  >
                    ✕
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Observed/Inferred HCP Sentiment */}
        <div className="form-group" style={{ borderTop: "1px solid var(--border)", paddingTop: 16 }}>
          <label className="form-label" style={{ marginBottom: 10, display: "block" }}>Observed/Inferred HCP Sentiment</label>
          <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
            {["Positive", "Neutral", "Negative"].map((s) => {
              const emoji = s === "Positive" ? "😃" : s === "Neutral" ? "😐" : "😟";
              return (
                <label key={s} style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", fontSize: 14 }}>
                  <input
                    type="radio"
                    name="sentiment"
                    value={s}
                    checked={sentiment.toLowerCase() === s.toLowerCase()}
                    onChange={(e) => setSentiment(e.target.value)}
                    style={{ cursor: "pointer", accentColor: "var(--primary)" }}
                  />
                  {emoji} {s}
                </label>
              );
            })}
          </div>
        </div>

        {/* Outcomes */}
        <div className="form-group" style={{ borderTop: "1px solid var(--border)", paddingTop: 16 }}>
          <label className="form-label">Outcomes</label>
          <textarea
            className="form-input"
            style={{ width: "100%" }}
            rows={3}
            value={outcomes}
            onChange={(e) => setOutcomes(e.target.value)}
            placeholder="Key outcomes or agreements..."
          />
        </div>

        {/* Action Items */}
        <div className="form-group">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
            <label className="form-label">Action Items</label>
            <button
              type="button"
              onClick={handleAddActionItem}
              style={{ background: "none", border: "none", color: "var(--primary)", fontSize: 12, cursor: "pointer", fontWeight: "bold" }}
            >
              + Add Action Item
            </button>
          </div>

          {actionItems.map((item, idx) => (
            <div key={idx} style={{ display: "flex", gap: 12, marginBottom: 8 }}>
              <input
                type="text"
                placeholder="Description"
                className="form-input"
                style={{ flexGrow: 1 }}
                value={item.description}
                onChange={(e) => handleActionItemChange(idx, "description", e.target.value)}
                required
              />
              <input
                type="date"
                className="form-input"
                style={{ width: 140 }}
                value={item.due_date}
                onChange={(e) => handleActionItemChange(idx, "due_date", e.target.value)}
              />
              <button
                type="button"
                onClick={() => handleRemoveActionItem(idx)}
                style={{ background: "none", border: "none", color: "var(--error)", cursor: "pointer" }}
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        {/* Proposed Follow-up Date */}
        <div className="form-group">
          <label className="form-label">Proposed Follow-up Date</label>
          <input
            type="date"
            className="form-input"
            style={{ width: "100%" }}
            value={followUpDate}
            onChange={(e) => setFollowUpDate(e.target.value)}
          />
        </div>
      </div>

      <div className="submit-container" style={{ marginTop: 24, display: "flex", justifyContent: "flex-end" }}>
        <button
          type="submit"
          className="login-btn"
          style={{ width: "100%", padding: 14 }}
          disabled={isStreaming || !selectedHcpId}
        >
          {isStreaming ? "Saving..." : "Save via AI Agent"}
        </button>
      </div>
    </form>
  );
}
export default StructuredInteractionForm;
