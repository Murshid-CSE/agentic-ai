import React from "react";
import {
  Building2,
  FileText,
  Mail,
  CreditCard,
  Clock,
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
} from "lucide-react";

export default function PaymentContext({ request, riskSignals = [] }) {
  if (!request) return null;

  const hasAccountChanged = riskSignals.some((s) => s.signal_type === "ACCOUNT_CHANGED");
  const hasDomainMismatch = riskSignals.some((s) => s.signal_type === "DOMAIN_MISMATCH");
  const isUrgent = request.urgency?.toLowerCase() === "urgent";

  return (
    <div className="vf-card invoice-card">
      {/* Top Invoice Header */}
      <div className="invoice-header-row">
        <div className="invoice-vendor-block">
          <div className="vendor-avatar">
            <Building2 size={22} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <h3 style={{ fontSize: "1.15rem", fontWeight: 800, color: "#ffffff" }}>
                {request.vendor_name || "Unknown Vendor"}
              </h3>
              <span
                style={{
                  fontSize: "0.72rem",
                  fontFamily: "var(--font-mono)",
                  background: "#1e293b",
                  color: "#cbd5e1",
                  padding: "0.15rem 0.5rem",
                  borderRadius: "6px",
                }}
              >
                {request.invoice_number || "INV-001"}
              </span>
            </div>
            <p style={{ fontSize: "0.76rem", color: "var(--text-dim)", marginTop: "2px" }}>
              Inbound Procurement Invoice Claim • Ref ID: {request.request_id}
            </p>
          </div>
        </div>

        <div className="invoice-amount-block">
          <span className="invoice-amount-label">Claimed Invoice Total</span>
          <div className="invoice-amount-val font-mono">
            ${Number(request.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </div>
        </div>
      </div>

      {/* Invoice Specification & Security Audit Specs */}
      <div className="invoice-specs-grid">
        {/* Specification 1: Sender Email & Domain */}
        <div className="spec-box">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="spec-label">Sender Email / Domain</span>
            {hasDomainMismatch ? (
              <span className="chip-anomaly">⚠️ Domain Mismatch</span>
            ) : (
              <span className="chip-match">✓ Matches Registry</span>
            )}
          </div>
          <div className="spec-val font-mono" title={request.sender_email || request.sender_domain}>
            <Mail size={14} color={hasDomainMismatch ? "#f43f5e" : "#10b981"} />
            <span style={{ color: hasDomainMismatch ? "#fb7185" : "inherit" }}>
              {request.sender_email || request.sender_domain}
            </span>
          </div>
          <span style={{ fontSize: "0.7rem", color: "var(--text-dim)" }}>
            {hasDomainMismatch
              ? "Conflicting domain (Potential lookalike / BEC spoofing)"
              : "Registered corporate communication channel"}
          </span>
        </div>

        {/* Specification 2: Destination Bank Account */}
        <div className="spec-box">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="spec-label">Target Payment Account</span>
            {hasAccountChanged ? (
              <span className="chip-anomaly">⚠️ Changed Account</span>
            ) : (
              <span className="chip-match">✓ Verified On File</span>
            )}
          </div>
          <div className="spec-val font-mono">
            <CreditCard size={14} color={hasAccountChanged ? "#f43f5e" : "#10b981"} />
            <span style={{ color: hasAccountChanged ? "#fb7185" : "inherit" }}>
              {request.requested_account}
            </span>
          </div>
          <span style={{ fontSize: "0.7rem", color: "var(--text-dim)" }}>
            {hasAccountChanged
              ? "Differs from organization's trusted disbursement account"
              : "Matches established payment profile"}
          </span>
        </div>

        {/* Specification 3: Urgency & Payment Terms */}
        <div className="spec-box">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span className="spec-label">Disbursement Urgency</span>
            {isUrgent ? (
              <span className="chip-anomaly" style={{ background: "rgba(245, 158, 11, 0.18)", color: "#fbbf24", borderColor: "rgba(245, 158, 11, 0.4)" }}>
                ⚠️ Social Pressure
              </span>
            ) : (
              <span className="chip-match">Normal Schedule</span>
            )}
          </div>
          <div className="spec-val">
            <Clock size={14} color={isUrgent ? "#f59e0b" : "#94a3b8"} />
            <span style={{ textTransform: "capitalize", color: isUrgent ? "#fbbf24" : "inherit" }}>
              {request.urgency || "standard"} Terms
            </span>
          </div>
          <span style={{ fontSize: "0.7rem", color: "var(--text-dim)" }}>
            {isUrgent
              ? "Urgent disbursement demands frequently accompany attacks"
              : "Standard net-30 business payment lifecycle"}
          </span>
        </div>
      </div>
    </div>
  );
}
