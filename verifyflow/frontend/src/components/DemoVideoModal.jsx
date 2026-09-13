import React, { useState, useEffect, useRef } from "react";
import {
  Play,
  Pause,
  RotateCcw,
  SkipForward,
  SkipBack,
  Video,
  Download,
  Volume2,
  VolumeX,
  X,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  GitBranch,
  BarChart3,
  Lock,
  Sparkles,
  Layers,
  ArrowRight,
  CheckCircle2,
  Zap,
} from "lucide-react";

export default function DemoVideoModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  const [currentScene, setCurrentScene] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [downloadUrl, setDownloadUrl] = useState(null);

  const videoContainerRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const timerRef = useRef(null);

  const SCENES = [
    {
      id: 0,
      title: "1. The $2.9B Crisis & Core Thesis",
      duration: 10,
      subtitle: "Why spam filters fail on Business Email Compromise",
      voiceText:
        "Every year, over 2.9 billion dollars is lost to Business Email Compromise. Traditional security relies on spam filters that guess if an email looks malicious. VerifyFlow is different: it is a pre-action verification agent that determines what must be verified before an irreversible payment can proceed.",
      content: (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", height: "100%", justifyContent: "center" }}>
          <div style={{ textAlign: "center" }}>
            <span style={{ fontSize: "0.85rem", color: "#f43f5e", fontWeight: 700, letterSpacing: "0.06em", textTransform: "uppercase" }}>
              The Problem: $2.9B Annual Financial Losses
            </span>
            <h2 style={{ fontSize: "1.8rem", fontWeight: 800, color: "#ffffff", marginTop: "0.35rem" }}>
              Spam Filters Cannot Prevent Executive Impersonation
            </h2>
            <p style={{ color: "#94a3b8", fontSize: "0.95rem", maxWidth: "700px", margin: "0.5rem auto 0" }}>
              Attackers register lookalike domains and request urgent bank account changes on legitimate vendor invoices.
            </p>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem", maxWidth: "800px", margin: "0 auto", width: "100%" }}>
            <div style={{ background: "rgba(244, 63, 94, 0.08)", border: "1px solid rgba(244, 63, 94, 0.3)", borderRadius: "12px", padding: "1.25rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#fb7185", fontWeight: 700, marginBottom: "0.5rem" }}>
                <AlertTriangle size={18} />
                <span>Traditional Phishing Classifiers</span>
              </div>
              <ul style={{ fontSize: "0.85rem", color: "#cbd5e1", lineHeight: 1.6, paddingLeft: "1.2rem" }}>
                <li>Guesses based on text patterns & spam keywords</li>
                <li>Fooled by authentic invoice templates</li>
                <li>Fails completely on legitimate mailbox takeovers</li>
                <li>Zero cross-examination against banking ledgers</li>
              </ul>
            </div>

            <div style={{ background: "rgba(16, 185, 129, 0.08)", border: "1px solid rgba(16, 185, 129, 0.35)", borderRadius: "12px", padding: "1.25rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#10b981", fontWeight: 700, marginBottom: "0.5rem" }}>
                <ShieldCheck size={18} />
                <span>VerifyFlow Pre-Action Sentinel</span>
              </div>
              <ul style={{ fontSize: "0.85rem", color: "#cbd5e1", lineHeight: 1.6, paddingLeft: "1.2rem" }}>
                <li>Bounded autonomous investigation agent</li>
                <li>Cross-checks vendor identity, domain & bank accounts</li>
                <li>Dynamic OODA loop with tamper-proof SQLite evidence</li>
                <li>Deterministic policy authorization (Zero LLM trust)</li>
              </ul>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 1,
      title: "2. The Hero BEC Investigation",
      duration: 14,
      subtitle: "Detecting lookalike domains & unverified bank account swaps",
      voiceText:
        "Now watch the agent in action. An invoice arrives for 125,000 dollars claiming to be from Acme Supplies. VerifyFlow ingests the claims and executes its OODA loop. It verifies Acme Supplies is a trusted vendor, but discovers the sender domain acme-payments.co conflicts with official records, and the bank account has changed. The deterministic policy gate blocks the payment immediately.",
      content: (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem", height: "100%", justifyContent: "center" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <span style={{ fontSize: "0.75rem", color: "#38bdf8", fontWeight: 700, textTransform: "uppercase" }}>
                Live Agent Execution Trace
              </span>
              <h3 style={{ fontSize: "1.4rem", fontWeight: 800, color: "#ffffff" }}>
                Case B: $125,000 Wire Transfer Request
              </h3>
            </div>
            <span style={{ background: "rgba(244, 63, 94, 0.2)", color: "#fb7185", border: "1px solid rgba(244,63,94,0.4)", padding: "0.3rem 0.8rem", borderRadius: "9999px", fontWeight: 700, fontSize: "0.8rem" }}>
              🚨 CRITICAL BEC THREAT
            </span>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: "1rem" }}>
            {/* OODA Milestone Flow */}
            <div style={{ background: "#0c1322", border: "1px solid #1e293b", borderRadius: "10px", padding: "1rem", display: "flex", flexDirection: "column", gap: "0.6rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", fontSize: "0.82rem", color: "#10b981" }}>
                <CheckCircle2 size={16} />
                <span>1. Ingest Invoice: Extracted $125,000 wire claim for Acme Supplies</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", fontSize: "0.82rem", color: "#10b981" }}>
                <CheckCircle2 size={16} />
                <span>2. Vendor Baseline: Verified Acme Supplies has 18 past transactions</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", fontSize: "0.82rem", color: "#f43f5e", fontWeight: 600 }}>
                <AlertTriangle size={16} />
                <span>3. Domain Audit: ⚠️ Mismatch! 'acme-payments.co' ≠ 'acme.in'</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", fontSize: "0.82rem", color: "#f43f5e", fontWeight: 600 }}>
                <AlertTriangle size={16} />
                <span>4. Bank Account Audit: 🚨 'BANK-ACME-999' ≠ registered 'BANK-ACME-001'</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", fontSize: "0.82rem", color: "#38bdf8" }}>
                <Lock size={16} />
                <span>5. Policy Authorization: Zero-Trust Invariant Enforced</span>
              </div>
            </div>

            {/* Final Verdict Card */}
            <div style={{ background: "radial-gradient(circle at top left, rgba(244, 63, 94, 0.2), transparent 70%), #140d18", border: "1px solid rgba(244, 63, 94, 0.5)", borderRadius: "10px", padding: "1.25rem", display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", color: "#f43f5e", fontWeight: 800, fontSize: "1.1rem" }}>
                  <ShieldAlert size={24} />
                  <span>BLOCKED — HELD FOR HUMAN REVIEW</span>
                </div>
                <p style={{ fontSize: "0.82rem", color: "#cbd5e1", marginTop: "0.5rem", lineHeight: 1.45 }}>
                  Unauthorized payment prevented. Both sender email domain and destination bank account conflict with verified vendor baseline records.
                </p>
              </div>

              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", paddingTop: "0.75rem", borderTop: "1px solid rgba(255,255,255,0.08)", fontSize: "0.78rem" }}>
                <span style={{ color: "#f43f5e", fontWeight: 700 }}>Risk Score: 100 / 100</span>
                <span style={{ color: "#94a3b8" }}>$125,000 Protected</span>
              </div>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 2,
      title: "3. Outage & Self-Healing AI Adaptation",
      duration: 14,
      subtitle: "Multi-step replanning when real-world APIs fail",
      voiceText:
        "In production, APIs go down. Most prototypes crash when a tool drops. VerifyFlow demonstrates true runtime adaptation. When the primary verification API suffers an outage, the agent detects the tool failure and replans its strategy. It automatically pivots to an independent secondary phone channel to contact the authorized CFO, safely resolving the ambiguity.",
      content: (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem", height: "100%", justifyContent: "center" }}>
          <div style={{ textAlign: "center" }}>
            <span style={{ fontSize: "0.75rem", color: "#c084fc", fontWeight: 700, textTransform: "uppercase" }}>
              Failure Handling & Self-Healing Replanning
            </span>
            <h3 style={{ fontSize: "1.45rem", fontWeight: 800, color: "#ffffff", marginTop: "0.2rem" }}>
              Intermediate Failure Becomes an Actionable State Transition
            </h3>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem" }}>
            {/* Step A: Tool Failure */}
            <div style={{ background: "#0c1322", border: "1px solid #1e293b", borderRadius: "10px", padding: "1.1rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "#f43f5e", fontWeight: 700, fontSize: "0.85rem", marginBottom: "0.4rem" }}>
                <AlertTriangle size={16} />
                <span>1. Tool Failure Injected</span>
              </div>
              <p style={{ fontSize: "0.78rem", color: "#94a3b8", lineHeight: 1.45 }}>
                Primary verification portal returns <code style={{ color: "#fb7185" }}>TOOL_UNAVAILABLE</code> (Simulated API outage).
              </p>
            </div>

            {/* Step B: Dynamic Replanning */}
            <div style={{ background: "rgba(168, 85, 247, 0.1)", border: "1px solid rgba(168, 85, 247, 0.4)", borderRadius: "10px", padding: "1.1rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "#c084fc", fontWeight: 700, fontSize: "0.85rem", marginBottom: "0.4rem" }}>
                <GitBranch size={16} />
                <span>2. Agent Replans Strategy</span>
              </div>
              <p style={{ fontSize: "0.78rem", color: "#e2e8f0", lineHeight: 1.45 }}>
                Agent triggers secondary out-of-band verification tool (<code style={{ color: "#c084fc" }}>verify_via_trusted_contact</code>).
              </p>
            </div>

            {/* Step C: Productive Recovery */}
            <div style={{ background: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.4)", borderRadius: "10px", padding: "1.1rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "#10b981", fontWeight: 700, fontSize: "0.85rem", marginBottom: "0.4rem" }}>
                <CheckCircle2 size={16} />
                <span>3. Self-Healing Recovery</span>
              </div>
              <p style={{ fontSize: "0.78rem", color: "#e2e8f0", lineHeight: 1.45 }}>
                Verified CFO confirms the bank account migration. Evidence recorded in SQLite, and payment is safely <strong>APPROVED</strong>.
              </p>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 3,
      title: "4. The 52-Scenario Benchmark Proof",
      duration: 14,
      subtitle: "Empirical proof: 0 false approvals vs 6 for one-shot LLMs",
      voiceText:
        "To rigorously prove VerifyFlow, we authored an independent benchmark of 52 controlled scenarios, including prompt injections, lookalikes, and edge cases. VerifyFlow achieved 100% accuracy with zero unsafe approvals. Meanwhile, an ungrounded LLM classifier suffered six critical false approvals.",
      content: (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem", height: "100%", justifyContent: "center" }}>
          <div style={{ textAlign: "center" }}>
            <span style={{ fontSize: "0.75rem", color: "#818cf8", fontWeight: 700, textTransform: "uppercase" }}>
              Quantitative Evaluation & Comparative Baseline
            </span>
            <h3 style={{ fontSize: "1.45rem", fontWeight: 800, color: "#ffffff", marginTop: "0.2rem" }}>
              52 Controlled Scenarios Across 5 Architectural Categories
            </h3>
          </div>

          <div style={{ background: "#0c1322", border: "1px solid #1e293b", borderRadius: "10px", overflow: "hidden" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.82rem", textAlign: "left" }}>
              <thead>
                <tr style={{ background: "#111a2f", borderBottom: "1px solid #1e293b", color: "#94a3b8" }}>
                  <th style={{ padding: "0.75rem 1rem" }}>Architecture</th>
                  <th style={{ padding: "0.75rem 1rem" }}>Accuracy</th>
                  <th style={{ padding: "0.75rem 1rem" }}>Unsafe Approvals</th>
                  <th style={{ padding: "0.75rem 1rem" }}>Avg Tools Used</th>
                  <th style={{ padding: "0.75rem 1rem" }}>Operational Result</th>
                </tr>
              </thead>
              <tbody>
                <tr style={{ borderBottom: "1px solid #1e293b" }}>
                  <td style={{ padding: "0.7rem 1rem", fontWeight: 600 }}>Static 6-Tool Pipeline</td>
                  <td style={{ padding: "0.7rem 1rem" }}>100%</td>
                  <td style={{ padding: "0.7rem 1rem", color: "#10b981" }}>0</td>
                  <td style={{ padding: "0.7rem 1rem", fontFamily: "var(--font-mono)" }}>6.00 (Fixed)</td>
                  <td style={{ padding: "0.7rem 1rem", color: "#94a3b8" }}>Brute force, high latency</td>
                </tr>
                <tr style={{ borderBottom: "1px solid #1e293b", background: "rgba(244, 63, 94, 0.05)" }}>
                  <td style={{ padding: "0.7rem 1rem", fontWeight: 600, color: "#fb7185" }}>One-Shot LLM Classifier</td>
                  <td style={{ padding: "0.7rem 1rem" }}>88.5%</td>
                  <td style={{ padding: "0.7rem 1rem", color: "#f43f5e", fontWeight: 800 }}>6 (CRITICAL FAIL)</td>
                  <td style={{ padding: "0.7rem 1rem", fontFamily: "var(--font-mono)" }}>0.00</td>
                  <td style={{ padding: "0.7rem 1rem", color: "#fb7185" }}>Fooled by prompt injection</td>
                </tr>
                <tr style={{ background: "rgba(16, 185, 129, 0.08)" }}>
                  <td style={{ padding: "0.7rem 1rem", fontWeight: 700, color: "#38bdf8" }}>VerifyFlow (Adaptive Agent)</td>
                  <td style={{ padding: "0.7rem 1rem", fontWeight: 700, color: "#10b981" }}>100%</td>
                  <td style={{ padding: "0.7rem 1rem", fontWeight: 800, color: "#10b981" }}>0 / 29 (0.00%)</td>
                  <td style={{ padding: "0.7rem 1rem", fontWeight: 700, color: "#38bdf8", fontFamily: "var(--font-mono)" }}>4.29 (-28.5%)</td>
                  <td style={{ padding: "0.7rem 1rem", fontWeight: 700, color: "#10b981" }}>Optimal efficiency & safety</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      ),
    },
    {
      id: 4,
      title: "5. Architecture & Deterministic Defense",
      duration: 10,
      subtitle: "Why VerifyFlow is safe: Untrusted input separated from authorization",
      voiceText:
        "Finally, here is why VerifyFlow cannot be tricked. The LLM is used only for extraction into strongly validated Pydantic schemas. Tool execution, risk scoring, evidence ledgering, and final authorization are 100% deterministic Python logic. Zero black-box trust. Thank you.",
      content: (
        <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", height: "100%", justifyContent: "center", textAlign: "center" }}>
          <div>
            <span style={{ fontSize: "0.75rem", color: "#10b981", fontWeight: 700, textTransform: "uppercase" }}>
              Defense-In-Depth Security Architecture
            </span>
            <h3 style={{ fontSize: "1.6rem", fontWeight: 800, color: "#ffffff", marginTop: "0.3rem" }}>
              Strict Separation Between LLM & Authorization
            </h3>
          </div>

          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.75rem", flexWrap: "wrap" }}>
            <div style={{ background: "#0c1322", border: "1px solid #1e293b", padding: "0.75rem 1rem", borderRadius: "8px", fontSize: "0.82rem", fontWeight: 600 }}>
              Untrusted Invoice
            </div>
            <ArrowRight size={16} color="#64748b" />
            <div style={{ background: "rgba(56, 189, 248, 0.1)", border: "1px solid rgba(56, 189, 248, 0.3)", padding: "0.75rem 1rem", borderRadius: "8px", fontSize: "0.82rem", fontWeight: 700, color: "#38bdf8" }}>
              LLM Extraction Only
            </div>
            <ArrowRight size={16} color="#64748b" />
            <div style={{ background: "#0c1322", border: "1px solid #1e293b", padding: "0.75rem 1rem", borderRadius: "8px", fontSize: "0.82rem", fontWeight: 600 }}>
              Pydantic Schemas
            </div>
            <ArrowRight size={16} color="#64748b" />
            <div style={{ background: "#0c1322", border: "1px solid #1e293b", padding: "0.75rem 1rem", borderRadius: "8px", fontSize: "0.82rem", fontWeight: 600 }}>
              Deterministic Tools
            </div>
            <ArrowRight size={16} color="#64748b" />
            <div style={{ background: "rgba(16, 185, 129, 0.15)", border: "1px solid rgba(16, 185, 129, 0.4)", padding: "0.75rem 1rem", borderRadius: "8px", fontSize: "0.82rem", fontWeight: 800, color: "#10b981" }}>
              Deterministic Policy Gate
            </div>
          </div>

          <div style={{ maxWidth: "680px", margin: "0 auto", background: "rgba(16, 185, 129, 0.05)", border: "1px solid rgba(16, 185, 129, 0.2)", borderRadius: "10px", padding: "0.85rem", fontSize: "0.82rem", color: "#cbd5e1" }}>
            🔒 <strong>Core Invariant:</strong> No prompt injection, adversarial wording, or LLM hallucination can ever bypass the hard-coded Python policy engine. Unverified bank changes can never execute without dual-channel authorization.
          </div>
        </div>
      ),
    },
  ];

  // Auto-play timer
  useEffect(() => {
    if (!isPlaying) {
      clearInterval(timerRef.current);
      return;
    }

    if (isVoiceEnabled && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(SCENES[currentScene].voiceText);
      utterance.rate = 1.05;
      window.speechSynthesis.speak(utterance);
    }

    timerRef.current = setTimeout(() => {
      if (currentScene < SCENES.length - 1) {
        setCurrentScene((prev) => prev + 1);
      } else {
        setIsPlaying(false);
      }
    }, SCENES[currentScene].duration * 1000);

    return () => {
      clearTimeout(timerRef.current);
      if ("speechSynthesis" in window) window.speechSynthesis.cancel();
    };
  }, [isPlaying, currentScene, isVoiceEnabled]);

  // Recording via canvas/MediaStream
  async function handleStartRecording() {
    try {
      if (!navigator.mediaDevices?.getDisplayMedia) {
        alert("Screen recording is supported directly via your browser or by using Loom / Windows Game Bar (Win+Alt+R).");
        return;
      }
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { cursor: "always" },
        audio: false,
      });

      const recorder = new MediaRecorder(stream, { mimeType: "video/webm;codecs=vp9" });
      const chunks = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: "video/webm" });
        const url = URL.createObjectURL(blob);
        setDownloadUrl(url);
        setIsRecording(false);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
      setIsPlaying(true);
      setCurrentScene(0);
    } catch (err) {
      console.error("Recording failed or cancelled:", err);
      setIsRecording(false);
    }
  }

  function handleStopRecording() {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }
  }

  return (
    <div className="modal-overlay" style={{ zIndex: 200 }}>
      <div
        className="modal-content"
        style={{
          maxWidth: "1080px",
          width: "95vw",
          height: "85vh",
          padding: "1.25rem 1.5rem",
          display: "flex",
          flexDirection: "column",
          gap: "0.85rem",
          background: "#080d19",
          border: "1px solid #283548",
          borderRadius: "16px",
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <div style={{ width: 34, height: 34, borderRadius: "8px", background: "linear-gradient(135deg, #2563eb, #7c3aed)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Video size={18} color="#ffffff" />
            </div>
            <div>
              <h2 style={{ fontSize: "1.1rem", fontWeight: 800, color: "#ffffff" }}>
                VerifyFlow — Interactive Demo Video Studio
              </h2>
              <p style={{ fontSize: "0.75rem", color: "var(--text-dim)" }}>
                Watch the official 5-scene narrated hackathon walkthrough or record an MP4/WebM video
              </p>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            {/* Audio Voiceover Toggle */}
            <button
              onClick={() => setIsVoiceEnabled(!isVoiceEnabled)}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "0.35rem",
                padding: "0.4rem 0.75rem",
                borderRadius: "8px",
                fontSize: "0.75rem",
                fontWeight: 600,
                border: "1px solid #334155",
                background: isVoiceEnabled ? "rgba(56, 189, 248, 0.15)" : "#0f172a",
                color: isVoiceEnabled ? "#38bdf8" : "#94a3b8",
                cursor: "pointer",
              }}
              title="Toggle AI voiceover speech synthesis"
            >
              {isVoiceEnabled ? <Volume2 size={14} /> : <VolumeX size={14} />}
              <span>{isVoiceEnabled ? "AI Voice: ON" : "AI Voice: OFF"}</span>
            </button>

            {/* Record / Download Button */}
            {!isRecording ? (
              <button
                className="btn btn-primary"
                onClick={handleStartRecording}
                style={{ fontSize: "0.78rem", padding: "0.4rem 0.85rem" }}
              >
                <Video size={14} />
                <span>Record Video File</span>
              </button>
            ) : (
              <button
                className="btn"
                onClick={handleStopRecording}
                style={{ background: "#f43f5e", color: "#fff", fontSize: "0.78rem", padding: "0.4rem 0.85rem" }}
              >
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#fff", animation: "pulse 1s infinite" }} />
                <span>Stop & Save Recording</span>
              </button>
            )}

            {downloadUrl && (
              <a
                href={downloadUrl}
                download="VerifyFlow_Demo_Walkthrough.webm"
                className="btn btn-accent"
                style={{ fontSize: "0.78rem", padding: "0.4rem 0.85rem" }}
              >
                <Download size={14} />
                <span>Download .webm</span>
              </a>
            )}

            <button onClick={onClose} style={{ background: "transparent", border: "none", color: "#94a3b8", cursor: "pointer", padding: "0.4rem" }}>
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Video Canvas Stage */}
        <div
          ref={videoContainerRef}
          style={{
            flex: 1,
            background: "linear-gradient(180deg, #0b1122 0%, #060913 100%)",
            border: "1px solid #1e293b",
            borderRadius: "12px",
            padding: "2rem",
            position: "relative",
            overflow: "hidden",
            boxShadow: "inset 0 0 40px rgba(0,0,0,0.6)",
          }}
        >
          {SCENES[currentScene].content}
        </div>

        {/* Teleprompter Subtitles */}
        <div style={{ background: "#0a0f1d", border: "1px solid #1a2338", borderRadius: "8px", padding: "0.6rem 1rem", fontSize: "0.8rem", color: "#e2e8f0", minHeight: "48px", display: "flex", alignItems: "center" }}>
          <span style={{ color: "#38bdf8", fontWeight: 700, marginRight: "0.5rem", flexShrink: 0 }}>
            NARRATION:
          </span>
          <span style={{ lineHeight: 1.4 }}>
            "{SCENES[currentScene].voiceText}"
          </span>
        </div>

        {/* Playback Controls & Scene Tabs */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", flexWrap: "wrap" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
            <button
              onClick={() => setCurrentScene((prev) => Math.max(0, prev - 1))}
              disabled={currentScene === 0}
              className="btn btn-secondary"
              style={{ padding: "0.4rem 0.6rem" }}
            >
              <SkipBack size={14} />
            </button>

            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="btn btn-primary"
              style={{ padding: "0.4rem 0.95rem" }}
            >
              {isPlaying ? <Pause size={14} /> : <Play size={14} />}
              <span>{isPlaying ? "Pause Demo" : "Auto-Play Demo"}</span>
            </button>

            <button
              onClick={() => setCurrentScene((prev) => Math.min(SCENES.length - 1, prev + 1))}
              disabled={currentScene === SCENES.length - 1}
              className="btn btn-secondary"
              style={{ padding: "0.4rem 0.6rem" }}
            >
              <SkipForward size={14} />
            </button>

            <button
              onClick={() => {
                setCurrentScene(0);
                setIsPlaying(false);
              }}
              className="btn btn-secondary"
              style={{ padding: "0.4rem 0.6rem" }}
              title="Restart from Scene 1"
            >
              <RotateCcw size={14} />
            </button>
          </div>

          {/* Scene Pill Selector */}
          <div style={{ display: "flex", gap: "0.3rem", flexWrap: "wrap" }}>
            {SCENES.map((scene, idx) => (
              <button
                key={scene.id}
                onClick={() => setCurrentScene(idx)}
                style={{
                  padding: "0.35rem 0.65rem",
                  borderRadius: "6px",
                  fontSize: "0.72rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  border: "none",
                  background: currentScene === idx ? "#2563eb" : "#0e1628",
                  color: currentScene === idx ? "#ffffff" : "#94a3b8",
                  transition: "all 0.15s ease",
                }}
              >
                Scene {idx + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
