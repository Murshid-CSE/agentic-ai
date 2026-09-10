import React from "react";
import {
  ShieldAlert,
  ShieldCheck,
  AlertOctagon,
  PauseCircle,
  Lock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
} from "lucide-react";

export default function DecisionReport({
  finalAction = "HUMAN_REVIEW",
  reason = "",
  riskSignals = [],
}) {
  const isApprove = finalAction === "APPROVE";
  const isReview = finalAction === "HUMAN_REVIEW";
  const isHold = finalAction === "HOLD";
  const isQuarantine = finalAction === "QUARANTINE";

  let title = "PAYMENT BLOCKED — HELD FOR REVIEW";
  let icon = <ShieldAlert size={28} color="#f43f5e" />;
  let colorClass = "decision-shield-HUMAN_REVIEW";
  let statusColor = "#f43f5e";
  let policyTag = "ZERO-TRUST INVARIANT: APPROVAL BLOCKED";

  if (isApprove) {
    title = "VERIFIED & APPROVED";
    icon = <ShieldCheck size={28} color="#10b981" />;
    colorClass = "decision-shield-APPROVE";
    statusColor = "#10b981";
    policyTag = "POLICY GATE: PERMITTED FOR PAYMENT";
  } else if (isHold) {
    title = "PAYMENT ON TEMPORARY HOLD";
    icon = <PauseCircle size={28} color="#eab308" />;
    colorClass = "decision-shield-HOLD";
    statusColor = "#eab308";
    policyTag = "POLICY GATE: INSUFFICIENT EVIDENCE";
  } else if (isQuarantine) {
    title = "SUSPICIOUS REQUEST QUARANTINED";
    icon = <AlertOctagon size={28} color="#e11d48" />;
    colorClass = "decision-shield-QUARANTINE";
    statusColor = "#e11d48";
    policyTag = "POLICY GATE: ADVERSARIAL ANOMALY";
  }

  // Derive human-readable bullet points
  const keyReasons = [];
  if (isApprove) {
    keyReasons.push("Sender identity matches trusted vendor communications records.");
    keyReasons.push("Destination bank account matches approved procurement profile.");
    keyReasons.push("Invoice amount complies with historical transaction baselines.");
  } else {
    if (riskSignals.some((s) => s.signal_type === "ACCOUNT_CHANGED")) {
      keyReasons.push("Target bank account differs from organization's registered vendor account.");
    }
    if (riskSignals.some((s) => s.signal_type === "DOMAIN_MISMATCH")) {
      keyReasons.push("Sender email domain conflicts with verified corporate identity domain.");
    }
    if (riskSignals.some((s) => s.signal_type === "VERIFICATION_UNAVAILABLE")) {
      keyReasons.push("Primary out-of-band verification channel is offline / unreachable.");
    }
    if (riskSignals.some((s) => s.signal_type === "VERIFICATION_FAILED")) {
      keyReasons.push("Executive contact repudiated the change or flagged potential fraud.");
    }
    if (riskSignals.some((s) => s.signal_type === "UNUSUAL_AMOUNT")) {
      keyReasons.push("Invoice amount exceeds historical baseline for this vendor.");
    }
    if (keyReasons.length === 0) {
      keyReasons.push("Deterministic policy rules prohibited automated payment authorization.");
    }
  }

  return (
    <div className={`decision-shield ${colorClass}`}>
      {/* Top Headline */}
      <div className="decision-top">
        <div className="decision-headline">
          <div className="decision-icon-badge">{icon}</div>
          <div>
            <div className="decision-title" style={{ color: statusColor }}>
              {title}
            </div>
            <p className="decision-summary">
              {reason ||
                (isApprove
                  ? "All autonomous identity and banking checks passed successfully."
                  : "VerifyFlow prohibited automated disbursement to protect enterprise capital.")}
            </p>
          </div>
        </div>

        {/* Policy Invariant Tag */}
        <div className="policy-invariant-badge" style={{ color: statusColor, border: `1px solid ${statusColor}40` }}>
          <Lock size={12} />
          <span>{policyTag}</span>
        </div>
      </div>

      {/* Checklist of Findings */}
      <div className="reasons-checklist">
        {keyReasons.map((item, index) => (
          <div key={index} className="reason-item">
            {isApprove ? (
              <CheckCircle2 size={15} color="#10b981" style={{ flexShrink: 0 }} />
            ) : (
              <XCircle size={15} color="#f43f5e" style={{ flexShrink: 0 }} />
            )}
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
