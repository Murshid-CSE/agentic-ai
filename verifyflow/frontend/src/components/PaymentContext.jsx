import React from "react";
import { Building, Hash, DollarSign, Mail, CreditCard, Clock, AlertCircle, CheckCircle2 } from "lucide-react";

export default function PaymentContext({ request, riskSignals }) {
  if (!request) return null;

  const hasAccountChanged = riskSignals?.some((s) => s.signal_type === "ACCOUNT_CHANGED");
  const hasDomainMismatch = riskSignals?.some((s) => s.signal_type === "DOMAIN_MISMATCH");
  const isUrgent = request.urgency?.toLowerCase() === "urgent";

  return (
    <div className="vf-card" style={{ background: "linear-gradient(180deg, #0f172a 0%, #0b1120 100%)" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.85rem" }}>
        <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Inbound Payment Request Metadata
        </span>
        <span style={{ fontSize: "0.72rem", color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
          Source: {request.sender_email || "invoice claim"}
        </span>
      </div>

      <div className="context-grid">
        {/* Vendor */}
        <div className="context-item">
          <span className="context-label">Vendor Entity</span>
          <div className="context-value">
            <Building size={16} color="#60a5fa" />
            <span>{request.vendor_name}</span>
          </div>
        </div>

        {/* Invoice Number */}
        <div className="context-item">
          <span className="context-label">Invoice Reference</span>
          <div className="context-value font-mono">
            <Hash size={15} color="#94a3b8" />
            <span>{request.invoice_number}</span>
          </div>
        </div>

        {/* Amount */}
        <div className="context-item">
          <span className="context-label">Claimed Amount</span>
          <div className="context-value font-mono" style={{ color: "#38bdf8", fontWeight: 700 }}>
            <DollarSign size={16} />
            <span>{Number(request.amount).toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
          </div>
        </div>

        {/* Sender Domain */}
        <div className="context-item">
          <span className="context-label">Sender Domain</span>
          <div className="context-value font-mono">
            <Mail size={15} color={hasDomainMismatch ? "#f43f5e" : "#10b981"} />
            <span style={{ color: hasDomainMismatch ? "#f43f5e" : "inherit" }}>
              {request.sender_domain}
            </span>
            {hasDomainMismatch && (
              <span style={{ fontSize: "0.65rem", padding: "0.1rem 0.35rem", borderRadius: "4px", background: "rgba(244, 63, 94, 0.15)", color: "#fb7185", fontWeight: 700 }}>
                LOOKALIKE
              </span>
            )}
          </div>
        </div>

        {/* Requested Bank Account */}
        <div className="context-item">
          <span className="context-label">Target Bank Account</span>
          <div className="context-value font-mono">
            <CreditCard size={15} color={hasAccountChanged ? "#f43f5e" : "#10b981"} />
            <span style={{ color: hasAccountChanged ? "#fb7185" : "inherit" }}>
              {request.requested_account}
            </span>
            {hasAccountChanged && (
              <span style={{ fontSize: "0.65rem", padding: "0.1rem 0.35rem", borderRadius: "4px", background: "rgba(244, 63, 94, 0.15)", color: "#fb7185", fontWeight: 700 }}>
                CHANGED
              </span>
            )}
          </div>
        </div>

        {/* Urgency */}
        <div className="context-item">
          <span className="context-label">Claimed Urgency</span>
          <div className="context-value">
            <Clock size={15} color={isUrgent ? "#f59e0b" : "#94a3b8"} />
            <span
              style={{
                fontSize: "0.75rem",
                fontWeight: 700,
                padding: "0.15rem 0.5rem",
                borderRadius: "4px",
                background: isUrgent ? "rgba(245, 158, 11, 0.15)" : "rgba(148, 163, 184, 0.1)",
                color: isUrgent ? "#fbbf24" : "#94a3b8",
                textTransform: "uppercase",
              }}
            >
              {request.urgency || "normal"}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
