import React from "react";
import { Sliders, CheckCircle, XCircle, PhoneCall, Radio, AlertOctagon } from "lucide-react";

export default function FailureInjectionBar({
  verificationAvailable,
  onToggleVerification,
  trustedContactState, // 'unreachable' | 'confirmed' | 'repudiated'
  onChangeTrustedContactState,
  enableSecondary,
  onToggleSecondary,
}) {
  return (
    <div
      className="vf-card"
      style={{
        background: "linear-gradient(90deg, #0b1120 0%, #111827 100%)",
        border: "1px dashed #334155",
        padding: "0.75rem 1.25rem",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: "0.85rem",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <Sliders size={16} color="#c084fc" />
        <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#f8fafc" }}>
          Failure Injection & Adaptation Switches:
        </span>
        <span style={{ fontSize: "0.7rem", color: "var(--text-dim)" }}>
          (Demonstrate real-time replanning by toggling runtime tool failures)
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
        {/* Switch 1: Primary Verification Service */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", fontWeight: 600 }}>
            Primary Verification:
          </span>
          <button
            type="button"
            onClick={onToggleVerification}
            style={{
              padding: "0.25rem 0.6rem",
              borderRadius: "6px",
              fontSize: "0.75rem",
              fontWeight: 700,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.3rem",
              background: verificationAvailable ? "rgba(16, 185, 129, 0.15)" : "rgba(244, 63, 94, 0.15)",
              color: verificationAvailable ? "#10b981" : "#f43f5e",
              border: `1px solid ${verificationAvailable ? "rgba(16, 185, 129, 0.4)" : "rgba(244, 63, 94, 0.4)"}`,
            }}
          >
            {verificationAvailable ? <CheckCircle size={13} /> : <XCircle size={13} />}
            <span>{verificationAvailable ? "ONLINE / AVAILABLE" : "OFFLINE / FAILING"}</span>
          </button>
        </div>

        {/* Switch 2: Secondary Contact Channel */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
          <span style={{ fontSize: "0.75rem", color: "#94a3b8", fontWeight: 600 }}>
            Secondary Contact (+91-9000000001):
          </span>
          <select
            value={trustedContactState}
            onChange={(e) => onChangeTrustedContactState(e.target.value)}
            style={{
              background: "#0b1120",
              border: "1px solid #334155",
              color:
                trustedContactState === "confirmed"
                  ? "#10b981"
                  : trustedContactState === "repudiated"
                  ? "#f43f5e"
                  : "#f59e0b",
              fontSize: "0.75rem",
              fontWeight: 700,
              padding: "0.25rem 0.5rem",
              borderRadius: "6px",
              cursor: "pointer",
            }}
          >
            <option value="unreachable">UNREACHABLE (Tool Failure)</option>
            <option value="confirmed">REACHABLE & CONFIRMED (Recovery)</option>
            <option value="repudiated">REACHABLE & REPUDIATED (Fraud Alert)</option>
          </select>
        </div>

        {/* Switch 3: Multi-step Adaptation Enabled */}
        <label style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.75rem", color: "#cbd5e1", cursor: "pointer" }}>
          <input
            type="checkbox"
            checked={enableSecondary}
            onChange={onToggleSecondary}
            style={{ cursor: "pointer" }}
          />
          <span>Enable 2-Tier Replanning</span>
        </label>
      </div>
    </div>
  );
}
