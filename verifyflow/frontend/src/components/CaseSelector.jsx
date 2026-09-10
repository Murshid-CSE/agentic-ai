import React from "react";
import {
  ShieldCheck,
  ShieldAlert,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  FolderOpen,
  DollarSign,
  ChevronRight,
} from "lucide-react";

export default function CaseSelector({
  presets,
  recentCases,
  selectedCaseId,
  onSelectCase,
}) {
  return (
    <div className="vf-card scenario-section">
      {/* Top Header */}
      <div className="scenario-header">
        <div>
          <h2 style={{ fontSize: "1.05rem", fontWeight: 800, color: "#ffffff", display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>Interactive Scenario Showcase</span>
            <span style={{ fontSize: "0.72rem", color: "var(--accent-cyan)", background: "rgba(6, 182, 212, 0.12)", padding: "0.15rem 0.5rem", borderRadius: "9999px", fontWeight: 700 }}>
              1-CLICK DEMOS
            </span>
          </h2>
          <p style={{ fontSize: "0.78rem", color: "var(--text-dim)", marginTop: "2px" }}>
            Select a real-world scenario to see how VerifyFlow investigates, detects threats, and adapts autonomously.
          </p>
        </div>

        {/* Historical Database Dropdown */}
        {recentCases && recentCases.length > 0 && (
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <FolderOpen size={14} color="var(--text-dim)" />
            <select
              value={selectedCaseId}
              onChange={(e) => {
                const found = recentCases.find((r) => r.request_id === e.target.value);
                if (found) onSelectCase(found);
              }}
              style={{
                background: "#080d1a",
                border: "1px solid #1e293b",
                color: "#cbd5e1",
                fontSize: "0.78rem",
                padding: "0.4rem 0.75rem",
                borderRadius: "8px",
                cursor: "pointer",
                maxWidth: "280px",
              }}
            >
              <option value="">Database History ({recentCases.length} records)...</option>
              {recentCases.map((rc) => (
                <option key={rc.investigation_id || rc.request_id} value={rc.request_id}>
                  {rc.request_id} — {rc.vendor_name} (${Number(rc.amount).toLocaleString()}) [{rc.final_action}]
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* 3 High-Impact Scenario Cards */}
      <div className="scenario-grid">
        {presets.map((c) => {
          const isSelected = selectedCaseId === c.request_id;
          const isSafe = c.expected_action === "APPROVE";
          const isAttack = c.scenarioType === "attack" || c.requested_account?.includes("999") || c.expected_score >= 80;
          const isRecovery = !isSafe && !isAttack;

          let badgeClass = "scenario-badge-safe";
          let badgeText = c.badge || "INSTANT AI APPROVAL";
          let icon = <ShieldCheck size={18} color="#10b981" />;

          if (isAttack) {
            badgeClass = "scenario-badge-attack";
            badgeText = c.badge || "CYBERATTACK BLOCKED";
            icon = <ShieldAlert size={18} color="#f43f5e" />;
          } else if (isRecovery) {
            badgeClass = "scenario-badge-recovery";
            badgeText = c.badge || "AUTONOMOUS ADAPTATION";
            icon = <Sparkles size={18} color="#c084fc" />;
          }

          return (
            <button
              key={c.request_id}
              className={`scenario-card ${isSelected ? "active" : ""}`}
              onClick={() => onSelectCase(c)}
            >
              <div className="scenario-card-top">
                <div className="scenario-icon-title">
                  {icon}
                  <span className="scenario-title">{c.label || c.request_id}</span>
                </div>
                <span className={`scenario-badge ${badgeClass}`}>{badgeText}</span>
              </div>

              <div className="scenario-meta">
                <span>{c.vendor_name}</span>
                <span className="scenario-amount">
                  ${Number(c.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>

              <p className="scenario-desc">
                {c.description || "Simulate automated verification for this payment claim."}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
