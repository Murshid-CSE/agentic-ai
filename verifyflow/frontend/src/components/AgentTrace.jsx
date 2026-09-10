import React, { useEffect, useRef } from "react";
import {
  Eye,
  Compass,
  Zap,
  Search,
  GitBranch,
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
} from "lucide-react";

export default function AgentTrace({
  trace = [],
  visibleCount = 999,
  isReplaying = false,
  adaptations = 0,
}) {
  const containerRef = useRef(null);

  // Auto-scroll to bottom as new steps appear during replay
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [visibleCount, trace]);

  const displayedSteps = trace.slice(0, visibleCount);

  function getPhaseMeta(phase, detail = "") {
    switch (phase) {
      case "OBSERVE":
        return {
          icon: <Eye size={16} />,
          badgeClass: "phase-OBSERVE",
          title: "OBSERVE",
        };
      case "DECIDE":
        return {
          icon: <Compass size={16} />,
          badgeClass: "phase-DECIDE",
          title: "DECIDE",
        };
      case "ACT":
        return {
          icon: <Zap size={16} />,
          badgeClass: "phase-ACT",
          title: "ACT",
        };
      case "EVALUATE":
        return {
          icon: <Search size={16} />,
          badgeClass: "phase-EVALUATE",
          title: "EVALUATE",
        };
      case "FAILURE":
        return {
          icon: <XCircle size={16} />,
          badgeClass: "phase-FAILURE",
          title: "FAILURE DETECTED",
        };
      case "ADAPT":
        return {
          icon: <GitBranch size={16} />,
          badgeClass: "phase-ADAPT",
          title: "ADAPT (REPLAN)",
        };
      case "FINAL":
        const isApprove = detail.startsWith("APPROVE");
        return {
          icon: isApprove ? <ShieldCheck size={16} /> : <ShieldAlert size={16} />,
          badgeClass: "phase-FINAL",
          title: "POLICY AUTHORIZATION",
        };
      default:
        return {
          icon: <Compass size={16} />,
          badgeClass: "phase-DECIDE",
          title: phase,
        };
    }
  }

  return (
    <div className="vf-card" style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      {/* Title & Stats */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div>
          <h3 style={{ fontSize: "1rem", fontWeight: 700, display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>Agent Investigation Trace</span>
            {isReplaying && (
              <span
                style={{
                  fontSize: "0.68rem",
                  color: "#38bdf8",
                  background: "rgba(56, 189, 248, 0.15)",
                  padding: "0.15rem 0.45rem",
                  borderRadius: "4px",
                  animation: "pulse 1.5s infinite",
                  fontWeight: 600,
                }}
              >
                ● REPLAYING STEP {visibleCount} OF {trace.length}
              </span>
            )}
          </h3>
          <p style={{ fontSize: "0.78rem", color: "var(--text-dim)" }}>
            Dynamic OODA cycle: Observe → Decide → Act → Evaluate → Adapt
          </p>
        </div>

        <div style={{ display: "flex", gap: "0.5rem" }}>
          {adaptations > 0 && (
            <span
              style={{
                fontSize: "0.75rem",
                fontWeight: 700,
                background: "rgba(168, 85, 247, 0.15)",
                color: "#c084fc",
                border: "1px solid rgba(168, 85, 247, 0.4)",
                padding: "0.2rem 0.6rem",
                borderRadius: "6px",
                display: "flex",
                alignItems: "center",
                gap: "0.3rem",
              }}
            >
              <GitBranch size={13} />
              {adaptations} Adaptation{adaptations > 1 ? "s" : ""}
            </span>
          )}
          <span
            style={{
              fontSize: "0.75rem",
              fontWeight: 600,
              background: "#1e293b",
              color: "#94a3b8",
              padding: "0.2rem 0.5rem",
              borderRadius: "6px",
              fontFamily: "var(--font-mono)",
            }}
          >
            {displayedSteps.length}/{trace.length} Steps
          </span>
        </div>
      </div>

      {/* Trace Timeline List */}
      <div className="trace-container" ref={containerRef} style={{ flex: 1 }}>
        {displayedSteps.length === 0 ? (
          <div style={{ padding: "2rem", textAlign: "center", color: "var(--text-dim)", fontSize: "0.85rem" }}>
            No trace events yet. Click "Run Investigation" or choose a scenario.
          </div>
        ) : (
          displayedSteps.map((step, idx) => {
            const meta = getPhaseMeta(step.phase, step.detail);
            const isAdapt = step.phase === "ADAPT";
            const isFinal = step.phase === "FINAL";

            return (
              <div
                key={idx}
                className="trace-step"
                style={{
                  animation: isReplaying && idx === displayedSteps.length - 1 ? "fadeIn 0.3s ease" : "none",
                }}
              >
                {/* Node circle */}
                <div className={`trace-node ${meta.badgeClass}`}>{meta.icon}</div>

                {/* Content Box */}
                <div
                  className="trace-content"
                  style={{
                    borderLeft: isAdapt ? "3px solid #a855f7" : isFinal ? "3px solid #f43f5e" : "1px solid #1e293b",
                    background: isAdapt
                      ? "rgba(168, 85, 247, 0.05)"
                      : isFinal
                      ? "rgba(244, 63, 94, 0.05)"
                      : "#0b1120",
                  }}
                >
                  <div className="trace-header">
                    <span className="trace-phase-badge" style={{ color: "var(--text-dim)" }}>
                      {meta.title}
                    </span>
                    {step.tool && <span className="trace-tool-tag font-mono">{step.tool}</span>}
                  </div>

                  <div
                    className="trace-detail"
                    style={{
                      fontWeight: isAdapt || isFinal ? 700 : 400,
                      color: isAdapt ? "#e9d5ff" : isFinal ? "#ffe4e6" : "#e2e8f0",
                    }}
                  >
                    {step.detail}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
