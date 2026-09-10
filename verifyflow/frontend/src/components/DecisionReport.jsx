import React from "react";
import { ShieldAlert, ShieldCheck, AlertOctagon, PauseCircle, Lock, ShieldCheckIcon } from "lucide-react";

export default function DecisionReport({
  finalAction = "HUMAN_REVIEW",
  reason = "",
  riskSignals = [],
}) {
  const isApprove = finalAction === "APPROVE";
  const isReview = finalAction === "HUMAN_REVIEW";
  const isHold = finalAction === "HOLD";
  const isQuarantine = finalAction === "QUARANTINE";

  let title = "HUMAN REVIEW REQUIRED";
  let icon = <ShieldAlert size={26} color="#f43f5e" />;
  let colorClass = "decision-HUMAN_REVIEW";
  let statusColor = "#f43f5e";
  let policyTag = "POLICY GATE: AUTOMATIC APPROVAL PROHIBITED";

  if (isApprove) {
    title = "PAYMENT APPROVED";
    icon = <ShieldCheck size={26} color="#10b981" />;
    colorClass = "decision-APPROVE";
    statusColor = "#10b981";
    policyTag = "POLICY GATE: PERMITTED ACTION";
  } else if (isHold) {
    title = "PAYMENT ON HOLD";
    icon = <PauseCircle size={26} color="#eab308" />;
    colorClass = "decision-HOLD";
    statusColor = "#eab308";
    policyTag = "POLICY GATE: INSUFFICIENT EVIDENCE FOR APPROVAL";
  } else if (isQuarantine) {
    title = "REQUEST QUARANTINED";
    icon = <AlertOctagon size={26} color="#e11d48" />;
    colorClass = "decision-QUARANTINE";
    statusColor = "#e11d48";
    policyTag = "POLICY GATE: ADVERSARIAL ANOMALY DETECTED";
  }

  // Derive explicit reason bullet points from signals if available
  const blockingReasons = [];
  if (riskSignals.some((s) => s.signal_type === "ACCOUNT_CHANGED")) {
    blockingReasons.push("Requested bank account differs from verified trusted vendor registry.");
  }
  if (riskSignals.some((s) => s.signal_type === "DOMAIN_MISMATCH")) {
    blockingReasons.push("Sender email domain does not match the vendor's registered identity domain.");
  }
  if (riskSignals.some((s) => s.signal_type === "VERIFICATION_UNAVAILABLE")) {
    blockingReasons.push("Independent verification through known out-of-band contact channel was unavailable.");
  }
  if (riskSignals.some((s) => s.signal_type === "VERIFICATION_FAILED")) {
    blockingReasons.push("Independent verification failed or repudiated by the vendor's trusted contact.");
  }
  if (riskSignals.some((s) => s.signal_type === "UNUSUAL_AMOUNT")) {
    blockingReasons.push("Claimed invoice amount exceeds historical maximum established for this vendor.");
  }
  if (riskSignals.some((s) => s.signal_type === "UNKNOWN_VENDOR")) {
    blockingReasons.push("Vendor was not located in the organization's trusted vendor registry.");
  }

  return (
    <div className={`vf-card decision-banner ${colorClass}`}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "0.75rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
          <div style={{ padding: "0.5rem", borderRadius: "10px", background: "rgba(0,0,0,0.3)" }}>
            {icon}
          </div>
          <div>
            <div style={{ fontSize: "1.2rem", fontWeight: 800, letterSpacing: "-0.02em", color: statusColor }}>
              {title}
            </div>
            <p style={{ fontSize: "0.85rem", color: "#e2e8f0", marginTop: "2px" }}>
              {reason || "Investigation resolved according to deterministic security policy rules."}
            </p>
          </div>
        </div>

        <div
          style={{
            fontSize: "0.72rem",
            fontWeight: 700,
            padding: "0.3rem 0.65rem",
            borderRadius: "6px",
            background: "rgba(0,0,0,0.4)",
            color: statusColor,
            border: `1px solid ${statusColor}40`,
            display: "flex",
            alignItems: "center",
            gap: "0.35rem",
            letterSpacing: "0.04em",
          }}
        >
          <Lock size={12} />
          {policyTag}
        </div>
      </div>

      {/* Blocking Reasons Breakdown */}
      {!isApprove && blockingReasons.length > 0 && (
        <div style={{ marginTop: "0.5rem", paddingTop: "0.75rem", borderTop: "1px solid rgba(255,255,255,0.08)" }}>
          <span style={{ fontSize: "0.75rem", fontWeight: 700, textTransform: "uppercase", color: "var(--text-dim)", letterSpacing: "0.05em" }}>
            Why Automatic Approval Was Blocked:
          </span>
          <ul style={{ listStyleType: "none", marginTop: "0.4rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
            {blockingReasons.map((item, idx) => (
              <li key={idx} style={{ display: "flex", alignItems: "baseline", gap: "0.5rem", fontSize: "0.82rem", color: "#f1f5f9" }}>
                <span style={{ color: statusColor, fontWeight: 700 }}>•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Security principle defense disclaimer */}
      <div
        style={{
          marginTop: "0.35rem",
          padding: "0.5rem 0.75rem",
          background: "rgba(0,0,0,0.3)",
          borderRadius: "6px",
          fontSize: "0.74rem",
          color: "var(--text-muted)",
          display: "flex",
          alignItems: "center",
          gap: "0.5rem",
        }}
      >
        <Lock size={13} color="#94a3b8" />
        <span>
          <strong>Zero LLM Authorization:</strong> Natural language was interpreted by the LLM layer, but the decision is strictly constrained by deterministic policy.
        </span>
      </div>
    </div>
  );
}
