import React from "react";
import {
  Sliders,
  CheckCircle,
  XCircle,
  PhoneCall,
  Radio,
  AlertOctagon,
  Sparkles,
  Zap,
} from "lucide-react";

export default function FailureInjectionBar({
  verificationAvailable,
  onToggleVerification,
  trustedContactState, // 'unreachable' | 'confirmed' | 'repudiated'
  onChangeTrustedContactState,
  enableSecondary,
  onToggleSecondary,
}) {
  return (
    <div className="vf-card chaos-simulator-card">
      {/* Top Header */}
      <div className="chaos-top-row">
        <div className="chaos-title">
          <Zap size={16} />
          <span>Live Resilience & Outage Simulator</span>
        </div>
        <span style={{ fontSize: "0.72rem", color: "var(--text-dim)" }}>
          Simulate real-world API outages to test agent replanning
        </span>
      </div>

      {/* Simulator Controls Grid */}
      <div className="chaos-controls-grid">
        {/* Control 1: Primary Verification Service */}
        <div className="chaos-box">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="chaos-box-label">Primary Verification API</span>
            <span style={{ fontSize: "0.68rem", color: verificationAvailable ? "#10b981" : "#f43f5e", fontWeight: 700 }}>
              {verificationAvailable ? "HEALTHY" : "OUTAGE"}
            </span>
          </div>

          <button
            type="button"
            onClick={onToggleVerification}
            style={{
              padding: "0.35rem 0.6rem",
              borderRadius: "6px",
              fontSize: "0.75rem",
              fontWeight: 700,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              gap: "0.35rem",
              background: verificationAvailable
                ? "rgba(16, 185, 129, 0.15)"
                : "rgba(244, 63, 94, 0.18)",
              color: verificationAvailable ? "#10b981" : "#f43f5e",
              border: `1px solid ${
                verificationAvailable ? "rgba(16, 185, 129, 0.4)" : "rgba(244, 63, 94, 0.45)"
              }`,
              transition: "all 0.15s ease",
            }}
          >
            {verificationAvailable ? <CheckCircle size={14} /> : <XCircle size={14} />}
            <span>{verificationAvailable ? "Online (Click to Fail)" : "Failing / Offline (Click to Restore)"}</span>
          </button>
        </div>

        {/* Control 2: Secondary Phone Contact */}
        <div className="chaos-box">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="chaos-box-label">Secondary CFO Phone Channel</span>
            <span
              style={{
                fontSize: "0.68rem",
                color:
                  trustedContactState === "confirmed"
                    ? "#10b981"
                    : trustedContactState === "repudiated"
                    ? "#f43f5e"
                    : "#f59e0b",
                fontWeight: 700,
              }}
            >
              {trustedContactState.toUpperCase()}
            </span>
          </div>

          <select
            value={trustedContactState}
            onChange={(e) => onChangeTrustedContactState(e.target.value)}
            style={{
              background: "#0c1322",
              border: "1px solid #1e293b",
              color:
                trustedContactState === "confirmed"
                  ? "#10b981"
                  : trustedContactState === "repudiated"
                  ? "#f43f5e"
                  : "#f59e0b",
              fontSize: "0.76rem",
              fontWeight: 700,
              padding: "0.35rem 0.5rem",
              borderRadius: "6px",
              cursor: "pointer",
              width: "100%",
            }}
          >
            <option value="unreachable">Phone Unreachable (Tool Failure)</option>
            <option value="confirmed">CFO Confirmed Change (Self-Heal & Approve)</option>
            <option value="repudiated">CFO Repudiated / Fraud Alert (Block)</option>
          </select>
        </div>
      </div>

      {/* Control 3: Multi-step Replanning Checkbox */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "0.4rem", borderTop: "1px solid rgba(255,255,255,0.06)" }}>
        <label style={{ display: "flex", alignItems: "center", gap: "0.45rem", fontSize: "0.76rem", color: "#cbd5e1", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={enableSecondary}
            onChange={onToggleSecondary}
            style={{ cursor: "pointer" }}
          />
          <span>Enable Autonomous Self-Healing / Multi-Step Replanning</span>
        </label>

        <span style={{ fontSize: "0.7rem", color: "var(--text-dim)" }}>
          {enableSecondary ? "Dynamic OODA loop enabled" : "Single-attempt mode"}
        </span>
      </div>
    </div>
  );
}
