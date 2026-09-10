import React, { useState } from "react";
import { AlertTriangle, Shield, CheckCircle, Database, Layers, Info } from "lucide-react";

export default function RiskPanel({
  riskScore = 0,
  riskLevel = "LOW",
  riskSignals = [],
  evidenceItems = [],
  toolCalls = [],
}) {
  const [activeTab, setActiveTab] = useState("signals"); // 'signals' | 'evidence' | 'tools'

  const scoreNum = Math.min(100, Math.max(0, Number(riskScore) || 0));

  function getLevelBadge(level) {
    const l = String(level).toUpperCase();
    if (l === "CRITICAL") return <span className="risk-level-badge badge-critical">CRITICAL RISK</span>;
    if (l === "HIGH") return <span className="risk-level-badge badge-high">HIGH RISK</span>;
    if (l === "MEDIUM") return <span className="risk-level-badge badge-medium">MEDIUM RISK</span>;
    return <span className="risk-level-badge badge-low">LOW RISK</span>;
  }

  function getBarColor(score) {
    if (score >= 76) return "linear-gradient(90deg, #f59e0b, #f43f5e)";
    if (score >= 46) return "linear-gradient(90deg, #eab308, #f97316)";
    if (score >= 16) return "linear-gradient(90deg, #10b981, #f59e0b)";
    return "#10b981";
  }

  return (
    <div className="vf-card" style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
      {/* Deterministic Risk Meter */}
      <div className="risk-gauge-container">
        <div className="risk-score-display">
          <div>
            <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-dim)", textTransform: "uppercase" }}>
              Deterministic Risk Score
            </span>
            <div className="risk-score-val font-mono" style={{ color: scoreNum >= 75 ? "#f43f5e" : scoreNum >= 45 ? "#f97316" : scoreNum >= 15 ? "#f59e0b" : "#10b981" }}>
              {scoreNum} <span style={{ fontSize: "1.1rem", color: "var(--text-dim)" }}>/ 100</span>
            </div>
          </div>
          <div>{getLevelBadge(riskLevel)}</div>
        </div>

        {/* Progress Bar */}
        <div className="risk-bar">
          <div
            className="risk-bar-fill"
            style={{
              width: `${scoreNum}%`,
              background: getBarColor(scoreNum),
            }}
          />
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.72rem", color: "var(--text-dim)" }}>
          <Info size={12} />
          <span>Prototype policy weights aggregating discrete verified evidence signals.</span>
        </div>
      </div>

      {/* Tabs */}
      <div>
        <div style={{ display: "flex", gap: "0.4rem", borderBottom: "1px solid #1e293b", paddingBottom: "0.4rem" }}>
          <button
            onClick={() => setActiveTab("signals")}
            style={{
              background: activeTab === "signals" ? "#1e293b" : "transparent",
              color: activeTab === "signals" ? "#f8fafc" : "var(--text-dim)",
              border: "none",
              padding: "0.35rem 0.75rem",
              borderRadius: "6px",
              fontSize: "0.8rem",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            <AlertTriangle size={13} />
            <span>Risk Signals ({riskSignals.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("evidence")}
            style={{
              background: activeTab === "evidence" ? "#1e293b" : "transparent",
              color: activeTab === "evidence" ? "#f8fafc" : "var(--text-dim)",
              border: "none",
              padding: "0.35rem 0.75rem",
              borderRadius: "6px",
              fontSize: "0.8rem",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            <Database size={13} />
            <span>Evidence Ledger ({evidenceItems.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("tools")}
            style={{
              background: activeTab === "tools" ? "#1e293b" : "transparent",
              color: activeTab === "tools" ? "#f8fafc" : "var(--text-dim)",
              border: "none",
              padding: "0.35rem 0.75rem",
              borderRadius: "6px",
              fontSize: "0.8rem",
              fontWeight: 600,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            <Layers size={13} />
            <span>Tool Calls ({toolCalls.length})</span>
          </button>
        </div>

        {/* Tab 1: Signals List */}
        {activeTab === "signals" && (
          <div className="signals-list">
            {riskSignals.length === 0 ? (
              <div style={{ padding: "1rem", textAlign: "center", color: "#10b981", fontSize: "0.82rem" }}>
                ✓ No adverse risk signals detected. All checks match trusted baseline records.
              </div>
            ) : (
              riskSignals.map((sig, idx) => (
                <div key={idx} className="signal-item">
                  <AlertTriangle
                    size={15}
                    color={sig.severity === "CRITICAL" ? "#f43f5e" : sig.severity === "HIGH" ? "#f97316" : "#f59e0b"}
                    style={{ flexShrink: 0, marginTop: "2px" }}
                  />
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <span style={{ fontWeight: 700, fontSize: "0.8rem", color: "#f8fafc" }}>
                        {sig.signal_type}
                      </span>
                      <span className="font-mono" style={{ fontSize: "0.75rem", color: "#f43f5e", fontWeight: 700 }}>
                        +{sig.score_weight} pts
                      </span>
                    </div>
                    <p style={{ fontSize: "0.78rem", color: "#cbd5e1", marginTop: "2px" }}>
                      {sig.description}
                    </p>
                    <span style={{ fontSize: "0.68rem", color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
                      Source: {sig.source_tool}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Tab 2: Evidence Ledger List */}
        {activeTab === "evidence" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", marginTop: "0.75rem", maxHeight: "320px", overflowY: "auto" }}>
            {evidenceItems.length === 0 ? (
              <div style={{ padding: "1rem", textAlign: "center", color: "var(--text-dim)", fontSize: "0.82rem" }}>
                No granular evidence items loaded.
              </div>
            ) : (
              evidenceItems.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "0.45rem 0.65rem",
                    background: "#0b1120",
                    border: "1px solid #1e293b",
                    borderRadius: "6px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    fontSize: "0.78rem",
                  }}
                >
                  <div>
                    <span style={{ color: "#93c5fd", fontWeight: 600 }} className="font-mono">
                      {item.key}
                    </span>
                    <span style={{ color: "var(--text-dim)", fontSize: "0.7rem", marginLeft: "0.5rem" }}>
                      [{item.tool_name}]
                    </span>
                  </div>
                  <div className="font-mono" style={{ color: "#e2e8f0", fontWeight: 600 }}>
                    {typeof item.value === "boolean"
                      ? item.value
                        ? "TRUE"
                        : "FALSE"
                      : String(item.value)}
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Tab 3: Tool Calls Audit */}
        {activeTab === "tools" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginTop: "0.75rem" }}>
            {toolCalls.length === 0 ? (
              <div style={{ padding: "1rem", textAlign: "center", color: "var(--text-dim)", fontSize: "0.82rem" }}>
                No tool executions recorded.
              </div>
            ) : (
              toolCalls.map((tc, idx) => (
                <div
                  key={idx}
                  style={{
                    padding: "0.55rem 0.75rem",
                    background: "#0b1120",
                    border: "1px solid #1e293b",
                    borderRadius: "6px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.2rem",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontWeight: 700, fontSize: "0.8rem", color: "#60a5fa" }} className="font-mono">
                      {tc.tool_name}
                    </span>
                    <span
                      style={{
                        fontSize: "0.7rem",
                        fontWeight: 700,
                        padding: "0.1rem 0.4rem",
                        borderRadius: "4px",
                        background:
                          tc.status === "SUCCESS"
                            ? "rgba(16, 185, 129, 0.15)"
                            : tc.status === "CONFLICT"
                            ? "rgba(245, 158, 11, 0.15)"
                            : "rgba(244, 63, 94, 0.15)",
                        color:
                          tc.status === "SUCCESS"
                            ? "#10b981"
                            : tc.status === "CONFLICT"
                            ? "#f59e0b"
                            : "#f43f5e",
                      }}
                    >
                      {tc.status}
                    </span>
                  </div>
                  <p style={{ fontSize: "0.76rem", color: "#cbd5e1" }}>{tc.summary}</p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
