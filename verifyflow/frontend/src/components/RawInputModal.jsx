import React, { useState } from "react";
import { X, Send, Sparkles, FileText } from "lucide-react";

export default function RawInputModal({ isOpen, onClose, onSubmitRaw }) {
  const [text, setText] = useState("");
  const [senderEmail, setSenderEmail] = useState("billing@acme-payments.co");
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const samples = [
    {
      label: "Sample 1: Direct Request",
      text: "Hi team, please use our new bank details for invoice 4938. Kindly transfer 125,000 to account BANK-ACME-999 today. Urgent month-end closure.",
    },
    {
      label: "Sample 2: Banking Partner Migration",
      text: "We've changed our banking partner to BANK-ACME-999. Kindly update the account and process invoice #4938 for 125000 USD right away, this is urgent.",
    },
    {
      label: "Sample 3: Account Deprecation Notice",
      text: "The old account is no longer active. Pay invoice 4938 ($125,000) to the account BANK-ACME-999 below. Urgent priority.",
    },
  ];

  async function handleSubmit(e) {
    e.preventDefault();
    if (!text.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmitRaw({
        text: text.trim(),
        sender_email: senderEmail.trim() || null,
        default_vendor: "Acme Supplies",
        verification_available: false,
      });
      onClose();
    } catch (err) {
      alert("Extraction failed: " + err.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <Sparkles size={18} color="#c084fc" />
            <h3 style={{ fontSize: "1.05rem", fontWeight: 700 }}>Test Natural Language Email Extraction</h3>
          </div>
          <button
            onClick={onClose}
            style={{ background: "transparent", border: "none", color: "var(--text-dim)", cursor: "pointer" }}
          >
            <X size={18} />
          </button>
        </div>

        <p style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
          Paste an unstructured email or memo. The LLM extracts entities and factual claims into a structured request, then the agent investigates deterministically.
        </p>

        {/* Quick sample buttons */}
        <div>
          <span style={{ fontSize: "0.72rem", color: "var(--text-dim)", textTransform: "uppercase", fontWeight: 700 }}>
            Quick Sample Wordings:
          </span>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.3rem" }}>
            {samples.map((s, idx) => (
              <button
                key={idx}
                type="button"
                className="btn btn-secondary"
                style={{ fontSize: "0.75rem", padding: "0.3rem 0.6rem" }}
                onClick={() => setText(s.text)}
              >
                <FileText size={12} />
                <span>{s.label}</span>
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          <div>
            <label style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-dim)" }}>
              Sender Email Header (optional)
            </label>
            <input
              type="email"
              value={senderEmail}
              onChange={(e) => setSenderEmail(e.target.value)}
              placeholder="e.g. billing@acme-payments.co"
              style={{
                width: "100%",
                background: "#0b1120",
                border: "1px solid #1e293b",
                borderRadius: "6px",
                padding: "0.5rem 0.75rem",
                color: "#f8fafc",
                fontSize: "0.82rem",
                fontFamily: "var(--font-mono)",
                marginTop: "0.25rem",
              }}
            />
          </div>

          <div>
            <label style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-dim)" }}>
              Raw Message Body
            </label>
            <textarea
              rows={4}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste payment change request text here..."
              required
              style={{
                width: "100%",
                background: "#0b1120",
                border: "1px solid #1e293b",
                borderRadius: "6px",
                padding: "0.6rem 0.75rem",
                color: "#f8fafc",
                fontSize: "0.85rem",
                marginTop: "0.25rem",
                resize: "vertical",
              }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.5rem", marginTop: "0.5rem" }}>
            <button type="button" className="btn btn-secondary" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={isSubmitting || !text.trim()}>
              <Send size={14} />
              <span>{isSubmitting ? "Extracting & Investigating..." : "Extract & Investigate"}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
