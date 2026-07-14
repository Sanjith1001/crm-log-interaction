interface ExtractedEntitiesPanelProps {
  entities: any;
}

export function ExtractedEntitiesPanel({ entities }: ExtractedEntitiesPanelProps) {
  if (!entities) return null;

  return (
    <div
      style={{
        marginTop: 12,
        padding: 16,
        backgroundColor: "rgba(20, 184, 166, 0.05)",
        border: "1px solid rgba(20, 184, 166, 0.2)",
        borderRadius: "var(--border-radius-sm)",
      }}
    >
      <h4 style={{ fontSize: 13, fontWeight: 600, color: "var(--primary)", marginBottom: 8 }}>
        ✨ Extracted Entities
      </h4>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, fontSize: 12 }}>
        {entities.hcp_name && (
          <div>
            <span style={{ color: "var(--text-secondary)" }}>HCP Name: </span>
            <strong>{entities.hcp_name}</strong>
          </div>
        )}
        {entities.visit_date && (
          <div>
            <span style={{ color: "var(--text-secondary)" }}>Visit Date: </span>
            <strong>{entities.visit_date}</strong>
          </div>
        )}
        {entities.products && entities.products.length > 0 && (
          <div style={{ gridColumn: "span 2" }}>
            <span style={{ color: "var(--text-secondary)" }}>Products: </span>
            <strong>{entities.products.join(", ")}</strong>
          </div>
        )}
        {entities.samples_given && entities.samples_given.length > 0 && (
          <div style={{ gridColumn: "span 2" }}>
            <span style={{ color: "var(--text-secondary)" }}>Samples: </span>
            <strong>
              {entities.samples_given.map((s: any) => `${s.product_name} (Qty: ${s.qty})`).join(", ")}
            </strong>
          </div>
        )}
        {entities.follow_up_date && (
          <div>
            <span style={{ color: "var(--text-secondary)" }}>Follow-up: </span>
            <strong>{entities.follow_up_date}</strong>
          </div>
        )}
      </div>
    </div>
  );
}
