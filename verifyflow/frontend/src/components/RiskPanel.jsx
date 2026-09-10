import React, { useState } from "react";
import {
  AlertTriangle,
  Shield,
  CheckCircle2,
  Database,
  Layers,
  Info,
  Key,
  Calendar,
  Lock,
} from "lucide-react";

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
    if (l === "CRITICAL") return <span className="risk-level-badge badge-critical">CRITICAL THREAT</span>;
    if (l === "HIGH") return <span className="risk-level-badge badge-high">HIGH RISK</span>;
    if (l === "MEDIUM") return <span className="risk-level-badge badge-medium">MEDIUM RISK</span>;
    return <span className="risk-level-badge badge-low">SAFE / LOW RISK</span>;
  }

  function getBarColor(score) {
    if (score >= 75) return "linear-gradient(90deg, #f59e0b, #f43f5e)";
    if (score >= 45) return "linear-gradient(90deg, #eab308, #f97316)";
    if (score >= 15) return "linear-gradient(90deg, #10b981, #f59e0b)";
    return "#10b981";
  }

  return (
    <div className="vf-card risk-card">
      {/* Risk Score & Gauge */}
      <div className="risk-meter-box">
        <div className="risk-meter-top">
          <div>
            <span style={{ fontSize: "0.72rem", fontWeight: 700, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Deterministic Risk Meter
            </span>
            <div
              className="risk-meter-score font-mono"
              style={{
                color:
                  scoreNum >= 75
                    ? "#f43f5e"
                    : scoreNum >= 45
                    ? "#f97316"
                    : scoreNum >= 15
                    ? "#f59e0b"
                    : "#10b981",
              }}
            >
              {scoreNum} <span className="risk-meter-denom">/ 100</span>
            </div>
          </div>
          <div>{getLevelBadge(riskLevel)}</div>
        </div>

        {/* Progress Bar */}
        <div className="risk-bar">
          <div
            className="risk-bar-fill"
            style={{
              width: `${Math.max(scoreNum, 3)}%`,
              background: getBarColor(scoreNum),
            }}
          />
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.74rem", color: "var(--text-dim)" }}>
          <Info size={13} />
          <span>Computed deterministically by Python rules; LLM has zero authorization authority.</span>
        </div>
      </div>

      {/* Tabs Header */}
      <div>
        <div style={{ display: "flex", gap: "0.35rem", borderBottom: "1px solid #1e293b", paddingBottom: "0.45rem" }}>
          <button
            onClick={() => setActiveTab("signals")}
            style={{
              background: activeTab === "signals" ? "#1e293b" : "transparent",
              color: activeTab === "signals" ? "#ffffff" : "var(--text-dim)",
              border: "none",
              padding: "0.35rem 0.75rem",
              borderRadius: "6px",
              fontSize: "0.78rem",
              fontWeight: 700,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            <AlertTriangle size={13} color={activeTab === "signals" ? "#f43f5e" : "currentColor"} />
            <span>Risk Signals ({riskSignals.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("evidence")}
            style={{
              background: activeTab === "evidence" ? "#1e293b" : "transparent",
              color: activeTab === "evidence" ? "#ffffff" : "var(--text-dim)",
              border: "none",
              padding: "0.35rem 0.75rem",
              borderRadius: "6px",
              fontSize: "0.78rem",
              fontWeight: 700,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            <Database size={13} color={activeTab === "evidence" ? "#38bdf8" : "currentColor"} />
            <span>Evidence Ledger ({evidenceItems.length})</span>
          </button>

          <button
            onClick={() => setActiveTab("tools")}
            style={{
              background: activeTab === "tools" ? "#1e293b" : "transparent",
              color: activeTab === "tools" ? "#ffffff" : "var(--text-dim)",
              border: "none",
              padding: "0.35rem 0.75rem",
              borderRadius: "6px",
              fontSize: "0.78rem",
              fontWeight: 700,
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "0.35rem",
            }}
          >
            <Layers size={13} color={activeTab === "tools" ? "#818cf8" : "currentColor"} />
            <span>Tools Run ({toolCalls.length})</span>
          </button>
        </div>

        {/* Tab 1: Risk Signals */}
        {activeTab === "signals" && (
          <div className="findings-list" style={{ marginTop: "0.75rem" }}>
            {riskSignals.length === 0 ? (
              <div style={{ textAlign: "center", padding: "1.5rem", color: "#10b981", fontSize: "0.82rem", background: "#080d1a", borderRadius: "8px", border: "1px solid #1e293b" }}>
                ✓ Zero risk signals detected. Clean transaction baseline.
              </div>
            ) : (
              riskSignals.map((sig, i) => {
                const isCrit = sig.severity === "CRITICAL";
                const isHigh = sig.severity === "HIGH";
                const isMed = sig.severity === "MEDIUM";

                let iconColor = "#10b981";
                if (isCrit) iconColor = "#f43f5e";
                else if (isHigh) iconColor = "#fb7185";
                else if (isMed) iconColor = "#f59e0b";

                return (
                  <div key={i} className="finding-row">
                    <AlertTriangle size={15} color={iconColor} style={{ flexShrink: 0, marginTop: "2px" }} />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <span style={{ fontWeight: 700, color: "#f8fafc", fontSize: "0.82rem" }}>
                          {sig.signal_type.replace(/_/g, " ")}
                        </span>
                        <div style={{ display: "flex", gap: "0.35rem", alignItems: "center" }}>
                          <span
                            style={{
                              fontSize: "0.68rem",
                              fontWeight: 700,
                              padding: "0.1rem 0.4rem",
                              borderRadius: "4px",
                              background: isCrit ? "rgba(244,63,94,0.2)" : "rgba(245,158,11,0.2)",
                              color: isCrit ? "#f43f5e" : "#f59e0b",
                            }}
                          >
                            {sig.severity}
                          </span>
                          <span style={{ fontSize: "0.72rem", fontFamily: "var(--font-mono)", color: "var(--text-dim)", fontWeight: 600 }}>
                            +{sig.score_weight} pts
                          </span>
                        </div>
                      </div>
                      <p style={{ fontSize: "0.76rem", color: "#94a3b8", marginTop: "2px" }}>
                        {sig.description}
                      </p>
                      {sig.source_tool && (
                        <span style={{ fontSize: "0.68rem", fontFamily: "var(--font-mono)", color: "var(--text-dim)" }}>
                          Source: {sig.source_tool}
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}

        {/* Tab 2: SQLite Evidence Ledger */}
        {activeTab === "evidence" && (
          <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {evidenceItems.length === 0 ? (
              <div style={{ textAlign: "center", padding: "1.5rem", color: "var(--text-dim)", fontSize: "0.82rem", background: "#080d1a", borderRadius: "8px", border: "1px solid #1e293b" }}>
                Evidence ledger records stored in SQLite database.
              </div>
            ) : (
              evidenceItems.map((ev, i) => (
                <div key={i} className="finding-row" style={{ flexDirection: "column", gap: "0.3rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", width: "100%" }}>
                    <span style={{ fontWeight: 700, fontSize: "0.78rem", color: "#38bdf8", fontFamily: "var(--font-mono)" }}>
                      {ev.key}
                    </span>
                    <span style={{ fontSize: "0.68rem", color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
                      {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : "recorded"}
                    </span>
                  </div>
                  <pre style={{ fontSize: "0.72rem", background: "#0c1322", padding: "0.4rem", borderRadius: "6px", color: "#cbd5e1", overflowX: "auto" }}>
                    {typeof ev.value === "string" ? ev.value : JSON.stringify(ev.value, null, 2)}
                  </pre>
                  {ev.checksum && (
                    <span style={{ fontSize: "0.65rem", fontFamily: "var(--font-mono)", color: "var(--text-dim)" }}>
                      Checksum: {ev.checksum.slice(0, 16)}...
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Tab 3: Tool Execution Records */}
        {activeTab === "tools" && (
          <div style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {toolCalls.length === 0 ? (
              <div style={{ textAlign: "center", padding: "1.5rem", color: "var(--text-dim)", fontSize: "0.82rem", background: "#080d1a", borderRadius: "8px", border: "1px solid #1e293b" }}>
                No tool audit logs recorded.
              </div>
            ) : (
              toolCalls.map((t, i) => (
                <div key={i} className="finding-row" style={{ justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <span style={{ fontWeight: 700, fontSize: "0.78rem", color: "#818cf8", fontFamily: "var(--font-mono)" }}>
                      {t.tool_name || t}
                    </span>
                    {t.latency_ms && (
                      <span style={{ fontSize: "0.68rem", color: "var(--text-dim)", marginLeft: "0.5rem" }}>
                        ({t.latency_ms} ms)
                      </span>
                    )}
                  </div>
                  <span
                    style={{
                      fontSize: "0.68rem",
                      fontWeight: 700,
                      padding: "0.15rem 0.45rem",
                      borderRadius: "4px",
                      background:
                        t.status === "SUCCESS"
                          ? "rgba(16, 185, 129, 0.15)"
                          : t.status === "CONFLICT"
                          ? "rgba(244, 63, 94, 0.15)"
                          : "rgba(245, 158, 11, 0.15)",
                      color:
                        t.status === "SUCCESS"
                          ? "#10b981"
                          : t.status === "CONFLICT"
                          ? "#f43f5e"
                          : "#f59e0b",
                    }}
                  >
                    {t.status || "OK"}
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
