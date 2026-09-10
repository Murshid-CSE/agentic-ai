import React from "react";
import { CheckCircle, AlertTriangle, HelpCircle, History } from "lucide-react";

export default function CaseSelector({
  presets,
  recentCases,
  selectedCaseId,
  onSelectCase,
}) {
  return (
    <div className="vf-card case-selector">
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--text-dim)", textTransform: "uppercase" }}>
          Scenarios:
        </span>
        <div className="preset-tabs">
          {presets.map((c) => {
            const isSelected = selectedCaseId === c.request_id;
            let icon = <HelpCircle size={14} color="#38bdf8" />;
            if (c.expected_action === "APPROVE") {
              icon = <CheckCircle size={14} color="#10b981" />;
            } else if (c.expected_action === "HUMAN_REVIEW" || c.expected_action === "QUARANTINE") {
              icon = <AlertTriangle size={14} color="#f43f5e" />;
            }

            return (
              <button
                key={c.request_id}
                className={`preset-tab ${isSelected ? "active" : ""}`}
                onClick={() => onSelectCase(c)}
              >
                {icon}
                <span>{c.label || c.request_id}</span>
                <span style={{ fontSize: "0.72rem", opacity: 0.8, fontFamily: "var(--font-mono)" }}>
                  ${Number(c.amount).toLocaleString()}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {recentCases && recentCases.length > 0 && (
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <History size={14} color="var(--text-dim)" />
          <select
            value={selectedCaseId}
            onChange={(e) => {
              const found = recentCases.find((r) => r.request_id === e.target.value);
              if (found) onSelectCase(found);
            }}
            style={{
              background: "#0b1120",
              border: "1px solid #1e293b",
              color: "#cbd5e1",
              fontSize: "0.82rem",
              padding: "0.4rem 0.6rem",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            <option value="">Historical Database Cases ({recentCases.length})...</option>
            {recentCases.map((rc) => (
              <option key={rc.investigation_id || rc.request_id} value={rc.request_id}>
                {rc.request_id} — {rc.vendor_name} (${Number(rc.amount).toLocaleString()}) [{rc.final_action}]
              </option>
            ))}
          </select>
        </div>
      )}
    </div>
  );
}
