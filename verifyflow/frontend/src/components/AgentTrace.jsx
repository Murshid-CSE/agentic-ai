import React, { useState, useEffect, useRef, useMemo } from "react";
import {
  FileText,
  Building,
  Mail,
  CreditCard,
  PhoneCall,
  ShieldAlert,
  ShieldCheck,
  Compass,
  Zap,
  Search,
  AlertTriangle,
  GitBranch,
  XCircle,
  Eye,
  CheckCircle2,
  Sparkles,
  Layers,
} from "lucide-react";

export default function AgentTrace({
  trace = [],
  visibleCount = 999,
  isReplaying = false,
  adaptations = 0,
}) {
  const [viewMode, setViewMode] = useState("story"); // 'story' | 'technical'
  const containerRef = useRef(null);

  // Auto-scroll when new steps appear during replay
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [visibleCount, trace, viewMode]);

  const displayedSteps = trace.slice(0, visibleCount);

  // Convert raw OODA trace steps into human-readable milestone checkpoints
  const storyMilestones = useMemo(() => {
    const milestones = [];

    // Helper to see if any displayed step mentions a tool or phase
    const hasStep = (fn) => displayedSteps.some(fn);
    const lastStepWith = (fn) => [...displayedSteps].reverse().find(fn);

    // 1. Invoice Ingestion
    if (hasStep((s) => s.tool === "parse_invoice" || s.detail?.toLowerCase().includes("invoice"))) {
      milestones.push({
        id: "ingest",
        icon: <FileText size={18} />,
        nodeClass: "story-node-success",
        title: "1. Ingest & Parse Invoice",
        summary: "Read inbound payment claim, extracted invoice number, claimed amount, and vendor entity.",
        status: "Completed",
      });
    }

    // 2. Vendor Baseline
    if (hasStep((s) => s.tool === "check_vendor_history" || s.detail?.toLowerCase().includes("vendor"))) {
      milestones.push({
        id: "vendor",
        icon: <Building size={18} />,
        nodeClass: "story-node-success",
        title: "2. Check Vendor Baseline",
        summary: "Verified vendor against organization records. Confirmed historical transaction baseline.",
        status: "Verified",
      });
    }

    // 3. Sender Domain Security
    if (hasStep((s) => s.tool === "check_domain")) {
      const conflict = hasStep((s) => s.tool === "check_domain" && (s.detail?.includes("CONFLICT") || s.detail?.includes("does not match")));
      milestones.push({
        id: "domain",
        icon: conflict ? <AlertTriangle size={18} /> : <Mail size={18} />,
        nodeClass: conflict ? "story-node-danger" : "story-node-success",
        title: "3. Sender Domain Identity Audit",
        summary: conflict
          ? "🚨 Warning: Sender domain does not match vendor's official registered domain (Lookalike / BEC risk)."
          : "✓ Sender email domain verified against vendor's authorized communication records.",
        status: conflict ? "Mismatch Detected" : "Passed",
      });
    }

    // 4. Bank Account Reconciliation
    if (hasStep((s) => s.tool === "compare_payment_account")) {
      const conflict = hasStep((s) => s.tool === "compare_payment_account" && (s.detail?.includes("CONFLICT") || s.detail?.includes("differs")));
      milestones.push({
        id: "account",
        icon: conflict ? <AlertTriangle size={18} /> : <CreditCard size={18} />,
        nodeClass: conflict ? "story-node-danger" : "story-node-success",
        title: "4. Destination Bank Account Check",
        summary: conflict
          ? "🚨 Threat: Bank account changed from registered account to an unverified new routing number."
          : "✓ Destination account matches established vendor payment profile on file.",
        status: conflict ? "Account Swapped" : "Verified",
      });
    }

    // 5. Failure Recovery & Adaptation
    const hasFailure = hasStep((s) => s.phase === "FAILURE" || s.phase === "ADAPT" || s.tool === "verify_via_trusted_contact");
    if (hasFailure) {
      const contactStep = lastStepWith((s) => s.tool === "verify_via_trusted_contact");
      const isConfirmed = contactStep && contactStep.detail?.includes("SUCCESS");

      milestones.push({
        id: "adaptation",
        icon: <GitBranch size={18} />,
        nodeClass: "story-node-adapt",
        title: "5. Autonomous Outage Recovery & Replanning",
        summary: isConfirmed
          ? "Primary verification channel was unavailable. Agent automatically adapted and verified the change via secondary phone confirmation with the authorized executive."
          : "Primary verification channel failed. Agent adapted: attempted secondary contact verification, but was unable to obtain trusted out-of-band confirmation.",
        status: isConfirmed ? "Self-Healed & Confirmed" : "Adaptation Attempted",
      });
    }

    // 6. Policy Gate Decision
    const finalStep = lastStepWith((s) => s.phase === "FINAL");
    if (finalStep) {
      const isApprove = finalStep.detail?.startsWith("APPROVE");
      milestones.push({
        id: "policy",
        icon: isApprove ? <ShieldCheck size={18} /> : <ShieldAlert size={18} />,
        nodeClass: isApprove ? "story-node-success" : "story-node-danger",
        title: "6. Deterministic Policy Gate",
        summary: isApprove
          ? "All safety conditions met or independently verified. Approved for scheduled disbursement."
          : "Policy Gate triggered: Automatic payment disbursement strictly prohibited. Held for human review.",
        status: isApprove ? "Payment Approved" : "Held for Review",
      });
    }

    return milestones;
  }, [displayedSteps]);

  function getTechPhaseBadge(phase) {
    switch (phase) {
      case "OBSERVE":
        return <span className="tech-phase-badge phase-OBSERVE">OBSERVE</span>;
      case "DECIDE":
        return <span className="tech-phase-badge phase-DECIDE">DECIDE</span>;
      case "ACT":
        return <span className="tech-phase-badge phase-ACT">ACT</span>;
      case "EVALUATE":
        return <span className="tech-phase-badge phase-EVALUATE">EVALUATE</span>;
      case "FAILURE":
        return <span className="tech-phase-badge phase-FAILURE">FAILURE</span>;
      case "ADAPT":
        return <span className="tech-phase-badge phase-ADAPT">ADAPT</span>;
      case "FINAL":
        return <span className="tech-phase-badge phase-FINAL">POLICY</span>;
      default:
        return <span className="tech-phase-badge">{phase}</span>;
    }
  }

  return (
    <div className="vf-card trace-card">
      {/* Top Header & View Toggle */}
      <div className="trace-top-bar">
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <h3 style={{ fontSize: "1.05rem", fontWeight: 800, color: "#ffffff" }}>
              AI Investigation Workflow
            </h3>
            {isReplaying && (
              <span
                style={{
                  fontSize: "0.68rem",
                  color: "#38bdf8",
                  background: "rgba(56, 189, 248, 0.15)",
                  padding: "0.15rem 0.55rem",
                  borderRadius: "9999px",
                  fontWeight: 700,
                  display: "flex",
                  alignItems: "center",
                  gap: "0.3rem",
                }}
              >
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#38bdf8" }} />
                STEP {visibleCount} OF {trace.length}
              </span>
            )}
          </div>
          <p style={{ fontSize: "0.76rem", color: "var(--text-dim)", marginTop: "2px" }}>
            {viewMode === "story"
              ? "Human-readable executive milestones extracted from live agent actions"
              : "Granular Observe → Decide → Act → Evaluate (OODA) runtime execution log"}
          </p>
        </div>

        {/* Story vs Technical Toggle */}
        <div className="view-mode-toggle">
          <button
            className={`toggle-btn ${viewMode === "story" ? "active" : ""}`}
            onClick={() => setViewMode("story")}
          >
            <Sparkles size={13} color={viewMode === "story" ? "#38bdf8" : "currentColor"} />
            <span>Story View</span>
          </button>

          <button
            className={`toggle-btn ${viewMode === "technical" ? "active" : ""}`}
            onClick={() => setViewMode("technical")}
          >
            <Layers size={13} color={viewMode === "technical" ? "#818cf8" : "currentColor"} />
            <span>Technical OODA ({displayedSteps.length})</span>
          </button>
        </div>
      </div>

      {/* Trace Timeline Body */}
      <div ref={containerRef} style={{ maxHeight: "560px", overflowY: "auto", paddingRight: "0.4rem" }}>
        {viewMode === "story" ? (
          /* Human-First Story Milestones */
          <div className="story-timeline">
            {storyMilestones.length === 0 ? (
              <div style={{ textAlign: "center", padding: "2rem", color: "var(--text-dim)", fontSize: "0.85rem" }}>
                Initializing investigation steps...
              </div>
            ) : (
              storyMilestones.map((m) => (
                <div key={m.id} className="story-step">
                  <div className={`story-node ${m.nodeClass}`}>{m.icon}</div>
                  <div className="story-body">
                    <div className="story-header">
                      <span className="story-title">{m.title}</span>
                      <span
                        style={{
                          fontSize: "0.68rem",
                          fontWeight: 700,
                          color:
                            m.status.includes("Mismatch") || m.status.includes("Swapped")
                              ? "#fb7185"
                              : m.status.includes("Held")
                              ? "#f43f5e"
                              : m.status.includes("Approved")
                              ? "#10b981"
                              : "#38bdf8",
                        }}
                      >
                        {m.status}
                      </span>
                    </div>
                    <p className="story-text">{m.summary}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        ) : (
          /* Technical OODA Log View */
          <div className="tech-trace-list">
            {displayedSteps.map((step, idx) => (
              <div key={idx} className="tech-step">
                <span style={{ fontSize: "0.7rem", fontFamily: "var(--font-mono)", color: "var(--text-dim)", minWidth: "22px" }}>
                  #{idx + 1}
                </span>
                {getTechPhaseBadge(step.phase)}
                <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: "0.15rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: "0.82rem", color: "#f8fafc", fontWeight: 500 }}>
                      {step.detail}
                    </span>
                    {step.tool && (
                      <span
                        style={{
                          fontSize: "0.7rem",
                          fontFamily: "var(--font-mono)",
                          background: "#1e293b",
                          padding: "0.1rem 0.45rem",
                          borderRadius: "4px",
                          color: "#94a3b8",
                        }}
                      >
                        {step.tool}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
