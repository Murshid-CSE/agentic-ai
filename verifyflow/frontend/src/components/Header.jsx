import React from "react";
import {
  ShieldCheck,
  RotateCcw,
  FileText,
  Activity,
  BarChart3,
  Layers,
  Sparkles,
  Zap,
  Video,
} from "lucide-react";

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
  onOpenDemoVideoModal,
}) {
  return (
    <header className="vf-card header-bar">
      {/* Brand Identity */}
      <div className="brand-section">
        <div className="brand-icon">
          <ShieldCheck size={26} color="#ffffff" />
        </div>
        <div>
          <div className="brand-title">
            VerifyFlow
            <span className="brand-tag">Autonomous AI Sentinel</span>
          </div>
          <p style={{ fontSize: "0.78rem", color: "var(--text-dim)", marginTop: "2px" }}>
            Self-Healing Agentic Payment Risk Verification & Deterministic Policy Enforcement
          </p>
        </div>
      </div>

      {/* Center & Right Controls */}
      <div className="controls-group">
        {/* Navigation Mode Switcher */}
        <div
          style={{
            display: "flex",
            background: "#080d1a",
            padding: "0.25rem",
            borderRadius: "10px",
            border: "1px solid #1e293b",
            gap: "0.25rem",
          }}
        >
          <button
            onClick={() => onToggleViewMode("investigation")}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.4rem 0.85rem",
              borderRadius: "7px",
              fontSize: "0.8rem",
              fontWeight: 700,
              cursor: "pointer",
              border: "none",
              background:
                viewMode === "investigation"
                  ? "linear-gradient(135deg, #2563eb, #1d4ed8)"
                  : "transparent",
              color: viewMode === "investigation" ? "#ffffff" : "var(--text-dim)",
              transition: "all 0.2s ease",
            }}
          >
            <Layers size={15} />
            <span>Investigation Center</span>
          </button>

          <button
            onClick={() => onToggleViewMode("benchmark")}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.4rem",
              padding: "0.4rem 0.85rem",
              borderRadius: "7px",
              fontSize: "0.8rem",
              fontWeight: 700,
              cursor: "pointer",
              border: "none",
              background:
                viewMode === "benchmark"
                  ? "linear-gradient(135deg, #7c3aed, #6d28d9)"
                  : "transparent",
              color: viewMode === "benchmark" ? "#ffffff" : "var(--text-dim)",
              transition: "all 0.2s ease",
            }}
          >
            <BarChart3 size={15} />
            <span>52-Scenario Benchmark</span>
            <span
              style={{
                fontSize: "0.68rem",
                background: "rgba(255,255,255,0.2)",
                padding: "0.1rem 0.4rem",
                borderRadius: "9999px",
                fontFamily: "var(--font-mono)",
              }}
            >
              100%
            </span>
          </button>
        </div>

        {/* Action Buttons for Investigation View */}
        {viewMode === "investigation" && (
          <>
            <button
              className="btn btn-secondary"
              onClick={onReplayTrace}
              disabled={isReplaying}
              title="Watch the agent execute its step-by-step reasoning cycle"
            >
              <RotateCcw size={14} className={isReplaying ? "animate-spin" : ""} />
              <span>{isReplaying ? "Replaying AI..." : "Replay AI Investigation"}</span>
            </button>

            <button
              className="btn btn-primary"
              onClick={onOpenRawModal}
              title="Paste an unformatted invoice email or natural language prompt"
            >
              <FileText size={14} />
              <span>Test Custom Invoice</span>
            </button>

            <button
              className="btn btn-accent"
              onClick={onOpenDemoVideoModal}
              style={{ background: "linear-gradient(135deg, #8b5cf6, #6366f1)", color: "#ffffff", border: "none" }}
              title="Watch or record the interactive 5-scene demo video presentation"
            >
              <Video size={14} />
              <span>🎬 Demo Video Studio</span>
            </button>
          </>
        )}

        {/* Backend & Ledger Status */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "0.45rem",
            fontSize: "0.76rem",
            padding: "0.35rem 0.75rem",
            borderRadius: "8px",
            background: isOnline ? "rgba(16, 185, 129, 0.12)" : "rgba(245, 158, 11, 0.12)",
            color: isOnline ? "#10b981" : "#f59e0b",
            border: `1px solid ${
              isOnline ? "rgba(16, 185, 129, 0.3)" : "rgba(245, 158, 11, 0.3)"
            }`,
            fontFamily: "var(--font-mono)",
            fontWeight: 600,
          }}
        >
          <span
            style={{
              width: 7,
              height: 7,
              borderRadius: "50%",
              background: isOnline ? "#10b981" : "#f59e0b",
              boxShadow: isOnline ? "0 0 8px #10b981" : "none",
            }}
          />
          <span>{isOnline ? "SENTINEL ONLINE" : "OFFLINE ENGINE"}</span>
        </div>
      </div>
    </header>
  );
}
