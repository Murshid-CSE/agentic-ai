import React from "react";
import { ShieldCheck, Play, RotateCcw, FileText, Activity, BarChart3, Layers } from "lucide-react";

export default function Header({
  activeCaseId,
  isOnline,
  isReplaying,
  viewMode = "investigation",
  benchmarkCount = 52,
  onToggleViewMode,
  onRunInvestigation,
  onReplayTrace,
  onOpenRawModal,
}) {
  return (
    <header className="vf-card header-bar">
      <div className="brand-section">
        <div className="brand-icon">
          <ShieldCheck size={24} color="#ffffff" />
        </div>
        <div>
          <div className="brand-title">
            VerifyFlow
            <span className="brand-tag">Agentic Security</span>
          </div>
          <p style={{ fontSize: "0.78rem", color: "var(--text-dim)" }}>
            Autonomous Payment Risk Verification & Deterministic Policy Enforcement
          </p>
        </div>
      </div>

      <div className="controls-group">
        {/* Navigation View Switcher */}
        <div
          style={{
            display: "flex",
            background: "#0f172a",
            padding: "0.25rem",
            borderRadius: "8px",
            border: "1px solid #334155",
            gap: "0.25rem",
          }}
        >
          <button
            onClick={() => onToggleViewMode("investigation")}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
              padding: "0.35rem 0.75rem",
              borderRadius: "6px",
              fontSize: "0.78rem",
              fontWeight: 600,
              cursor: "pointer",
              border: "none",
              background: viewMode === "investigation" ? "var(--accent-blue)" : "transparent",
              color: viewMode === "investigation" ? "#ffffff" : "var(--text-dim)",
              transition: "all 0.15s ease",
            }}
          >
            <Layers size={14} />
            <span>Investigation Center</span>
          </button>

          <button
            onClick={() => onToggleViewMode("benchmark")}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
              padding: "0.35rem 0.75rem",
              borderRadius: "6px",
              fontSize: "0.78rem",
              fontWeight: 600,
              cursor: "pointer",
              border: "none",
              background: viewMode === "benchmark" ? "#8b5cf6" : "transparent",
              color: viewMode === "benchmark" ? "#ffffff" : "var(--text-dim)",
              transition: "all 0.15s ease",
            }}
          >
            <BarChart3 size={14} />
            <span>Benchmark Suite ({benchmarkCount})</span>
          </button>
        </div>

        {/* Backend Connectivity Badge */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.4rem",
            fontSize: "0.78rem",
            padding: "0.3rem 0.65rem",
            borderRadius: "6px",
            background: isOnline ? "rgba(16, 185, 129, 0.1)" : "rgba(245, 158, 11, 0.1)",
            color: isOnline ? "#10b981" : "#f59e0b",
            border: `1px solid ${isOnline ? "rgba(16, 185, 129, 0.3)" : "rgba(245, 158, 11, 0.3)"}`,
            fontFamily: "var(--font-mono)",
            fontWeight: 600,
          }}
        >
          <Activity size={13} className={isOnline ? "animate-pulse" : ""} />
          {isOnline ? "API Online" : "Local Prototype Mode"}
        </div>

        {viewMode === "investigation" && (
          <>
            {/* Active Case ID Badge */}
            <div
              style={{
                fontSize: "0.82rem",
                fontWeight: 700,
                padding: "0.35rem 0.75rem",
                borderRadius: "6px",
                background: "#1e293b",
                color: "#93c5fd",
                border: "1px solid #334155",
                fontFamily: "var(--font-mono)",
              }}
            >
              CASE #{activeCaseId || "VF-HERO"}
            </div>

            {/* Raw Message Test Modal */}
            <button className="btn btn-secondary" onClick={onOpenRawModal}>
              <FileText size={15} />
              <span>Raw Email Test</span>
            </button>

            {/* Replay Trace Animation */}
            <button className="btn btn-secondary" onClick={onReplayTrace} disabled={isReplaying}>
              <RotateCcw size={15} />
              <span>Replay Trace</span>
            </button>

            {/* Run / Re-run Investigation */}
            <button className="btn btn-primary" onClick={onRunInvestigation} disabled={isReplaying}>
              <Play size={15} />
              <span>Run Investigation</span>
            </button>
          </>
        )}
      </div>
    </header>
  );
}

