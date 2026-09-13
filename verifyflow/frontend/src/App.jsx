import React, { useState, useEffect, useRef } from "react";
import Header from "./components/Header";
import CaseSelector from "./components/CaseSelector";
import PaymentContext from "./components/PaymentContext";
import AgentTrace from "./components/AgentTrace";
import RiskPanel from "./components/RiskPanel";
import DecisionReport from "./components/DecisionReport";
import RawInputModal from "./components/RawInputModal";
import FailureInjectionBar from "./components/FailureInjectionBar";
import BenchmarkDashboard from "./components/BenchmarkDashboard";
import DemoVideoModal from "./components/DemoVideoModal";
import {
  checkHealth,
  fetchDemoCases,
  fetchRecentCases,
  runInvestigation,
  runRawInvestigation,
  fetchCaseEvidence,
  fetchBenchmarkResults,
  runBenchmark,
  FALLBACK_DEMO_CASES,
} from "./services/api";

export default function App() {
  const [viewMode, setViewMode] = useState("investigation"); // "investigation" | "benchmark"
  const [isOnline, setIsOnline] = useState(false);
  const [presets, setPresets] = useState(FALLBACK_DEMO_CASES);
  const [recentCases, setRecentCases] = useState([]);
  const [activeCase, setActiveCase] = useState(FALLBACK_DEMO_CASES[1]); // Default: Case B Hero
  const [investigation, setInvestigation] = useState(null);
  const [evidenceDetails, setEvidenceDetails] = useState({ tool_calls: [], evidence_items: [] });

  // M7 Benchmark Suite State
  const [benchmarkSummary, setBenchmarkSummary] = useState(null);
  const [isBenchmarkLoading, setIsBenchmarkLoading] = useState(false);

  // M6 Failure Injection Switches
  const [verificationAvailable, setVerificationAvailable] = useState(false);
  const [trustedContactState, setTrustedContactState] = useState("unreachable"); // 'unreachable' | 'confirmed' | 'repudiated'
  const [enableSecondary, setEnableSecondary] = useState(true);

  // Replay animation state
  const [visibleStepCount, setVisibleStepCount] = useState(999);
  const [isReplaying, setIsReplaying] = useState(false);
  const [isRawModalOpen, setIsRawModalOpen] = useState(false);
  const [isDemoVideoModalOpen, setIsDemoVideoModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const replayTimerRef = useRef(null);

  // Initialize data on mount
  useEffect(() => {
    async function init() {
      const online = await checkHealth();
      setIsOnline(online);

      if (online) {
        const demoCases = await fetchDemoCases();
        setPresets(demoCases);
        const history = await fetchRecentCases();
        setRecentCases(history);
        const bench = await fetchBenchmarkResults();
        if (bench) setBenchmarkSummary(bench);
      }

      // Automatically run default hero case
      executeInvestigation(FALLBACK_DEMO_CASES[1], true);
    }
    init();
    return () => clearInterval(replayTimerRef.current);
  }, []);

  async function handleTriggerBenchmark() {
    setIsBenchmarkLoading(true);
    try {
      const fresh = await runBenchmark();
      setBenchmarkSummary(fresh);
    } catch (err) {
      console.error("Failed to run benchmark:", err);
    } finally {
      setIsBenchmarkLoading(false);
    }
  }

  function handleInspectBenchmarkCase(benchmarkCase) {
    const rawReq = benchmarkCase.request || {
      request_id: benchmarkCase.case_id,
      vendor_name: benchmarkCase.name.split(" - ")[0] || "Acme Supplies",
      sender_email: "billing@domain.com",
      sender_domain: "domain.com",
      invoice_number: "INV-BENCH",
      amount: 50000,
      requested_account: "BANK-001",
      urgency: "normal",
    };
    const runtimeCfg = benchmarkCase.runtime_config || {};
    setViewMode("investigation");
    executeInvestigation(rawReq, true, {
      verification_available: runtimeCfg.verification_available ?? false,
      enable_secondary: runtimeCfg.enable_secondary_verification ?? false,
      trustedContactState:
        runtimeCfg.trusted_contact_confirmed === true
          ? "confirmed"
          : runtimeCfg.trusted_contact_confirmed === false
          ? "repudiated"
          : "unreachable",
    });
  }

  async function executeInvestigation(caseData, animate = true, overrideOptions = {}) {
    setIsLoading(true);
    setActiveCase(caseData);

    const payload = {
      request_id: caseData.request_id || "VF-001",
      vendor_name: caseData.vendor_name,
      sender_email: caseData.sender_email || "billing@domain.com",
      sender_domain: caseData.sender_domain || "domain.com",
      invoice_number: caseData.invoice_number || "INV-001",
      amount: Number(caseData.amount) || 1000,
      requested_account: caseData.requested_account || "BANK-001",
      urgency: caseData.urgency || "normal",
    };

    const options = {
      verification_available:
        overrideOptions.verification_available !== undefined
          ? overrideOptions.verification_available
          : verificationAvailable,
      enable_secondary_verification:
        overrideOptions.enable_secondary !== undefined
          ? overrideOptions.enable_secondary
          : enableSecondary,
      trusted_contact_reachable:
        (overrideOptions.trustedContactState || trustedContactState) !== "unreachable",
      trusted_contact_confirmed:
        (overrideOptions.trustedContactState || trustedContactState) === "confirmed"
          ? true
          : (overrideOptions.trustedContactState || trustedContactState) === "repudiated"
          ? false
          : null,
    };

    try {
      let result;
      if (isOnline) {
        result = await runInvestigation(payload, options);
        try {
          const evData = await fetchCaseEvidence(result.request_id);
          setEvidenceDetails(evData);
        } catch {
          // fallback to result evidence
        }
      } else {
        // Offline prototype simulation
        result = simulateOfflineInvestigation(caseData, options);
      }

      setInvestigation(result);

      if (animate && result.trace?.length > 0) {
        startReplay(result.trace.length);
      } else {
        setVisibleStepCount(result.trace?.length || 999);
        setIsReplaying(false);
      }

      // Refresh recent cases
      if (isOnline) {
        fetchRecentCases().then(setRecentCases);
      }
    } catch (err) {
      console.error("Investigation failed:", err);
      // Fallback
      const sim = simulateOfflineInvestigation(caseData, options);
      setInvestigation(sim);
      setVisibleStepCount(sim.trace.length);
    } finally {
      setIsLoading(false);
    }
  }

  function startReplay(totalSteps) {
    clearInterval(replayTimerRef.current);
    setIsReplaying(true);
    setVisibleStepCount(1);

    let current = 1;
    replayTimerRef.current = setInterval(() => {
      current += 1;
      setVisibleStepCount(current);
      if (current >= totalSteps) {
        clearInterval(replayTimerRef.current);
        setIsReplaying(false);
      }
    }, 280); // Step delay in ms
  }

  function handleReplayClick() {
    if (investigation?.trace?.length > 0) {
      startReplay(investigation.trace.length);
    }
  }

  async function handleRawSubmit(rawPayload) {
    setIsLoading(true);
    try {
      let result;
      const options = {
        enable_secondary_verification: enableSecondary,
        trusted_contact_reachable: trustedContactState !== "unreachable",
        trusted_contact_confirmed:
          trustedContactState === "confirmed" ? true : trustedContactState === "repudiated" ? false : null,
      };

      if (isOnline) {
        result = await runRawInvestigation(rawPayload, options);
        try {
          const evData = await fetchCaseEvidence(result.request_id);
          setEvidenceDetails(evData);
        } catch {}
      } else {
        result = simulateOfflineInvestigation(
          {
            request_id: rawPayload.request_id || "VF-RAW",
            vendor_name: "Acme Supplies",
            sender_email: rawPayload.sender_email || "billing@acme-payments.co",
            sender_domain: "acme-payments.co",
            invoice_number: "INV-4938",
            amount: 125000,
            requested_account: "BANK-ACME-999",
            urgency: "urgent",
          },
          options
        );
      }

      setActiveCase({
        request_id: result.request_id,
        vendor_name: "Acme Supplies",
        sender_email: rawPayload.sender_email || "billing@acme-payments.co",
        sender_domain: "acme-payments.co",
        invoice_number: "INV-4938",
        amount: 125000,
        requested_account: "BANK-ACME-999",
        urgency: "urgent",
      });

      setInvestigation(result);
      startReplay(result.trace?.length || 1);
    } finally {
      setIsLoading(false);
    }
  }

  // Generate simulated response if backend is offline
  function simulateOfflineInvestigation(c, opts = {}) {
    const isHero = c.requested_account?.includes("999") || c.amount > 75000;
    const isClean = c.expected_action === "APPROVE" || (!isHero && c.amount <= 50000);

    if (isClean) {
      return {
        request_id: c.request_id,
        final_action: "APPROVE",
        reason: "Vendor, sender domain, and payment account match trusted records.",
        risk_score: 0,
        risk_level: "LOW",
        adaptations: 0,
        tools_used: ["parse_invoice", "check_vendor_history", "check_domain", "compare_payment_account"],
        evidence: [],
        risk_signals: [],
        failures: [],
        trace: [
          { phase: "OBSERVE", detail: `New payment request ${c.request_id} received` },
          { phase: "DECIDE", detail: "Extract and validate invoice metadata", tool: "parse_invoice" },
          { phase: "ACT", detail: "parse_invoice → SUCCESS", tool: "parse_invoice" },
          { phase: "EVALUATE", detail: "Payment request contains the required invoice metadata.", tool: "parse_invoice" },
          { phase: "DECIDE", detail: "Establish trusted vendor baseline", tool: "check_vendor_history" },
          { phase: "ACT", detail: "check_vendor_history → SUCCESS", tool: "check_vendor_history" },
          { phase: "EVALUATE", detail: "Vendor exists in the trusted registry.", tool: "check_vendor_history" },
          { phase: "DECIDE", detail: "Verify sender domain against known vendor domain", tool: "check_domain" },
          { phase: "ACT", detail: "check_domain → SUCCESS", tool: "check_domain" },
          { phase: "EVALUATE", detail: "Sender domain matches the trusted vendor domain.", tool: "check_domain" },
          { phase: "DECIDE", detail: "Check for payment account changes", tool: "compare_payment_account" },
          { phase: "ACT", detail: "compare_payment_account → SUCCESS", tool: "compare_payment_account" },
          { phase: "EVALUATE", detail: "Requested payment account matches the trusted account.", tool: "compare_payment_account" },
          { phase: "DECIDE", detail: "Evidence collection complete" },
          { phase: "FINAL", detail: "APPROVE: Vendor, sender domain, and payment account match trusted records." },
        ],
      };
    }

    const isContactConfirmed = opts.trusted_contact_confirmed === true;
    const finalAction = isContactConfirmed ? "APPROVE" : "HUMAN_REVIEW";
    const reason = isContactConfirmed
      ? "Payment account changed but independently verified via secondary trusted contact."
      : "Payment account changed and independent verification did not confirm the request.";

    return {
      request_id: c.request_id,
      final_action: finalAction,
      reason: reason,
      risk_score: isContactConfirmed ? 40 : 100,
      risk_level: isContactConfirmed ? "MEDIUM" : "CRITICAL",
      adaptations: opts.enable_secondary_verification ? 2 : 1,
      tools_used: opts.enable_secondary_verification
        ? ["parse_invoice", "check_vendor_history", "check_domain", "compare_payment_account", "request_independent_verification", "verify_via_trusted_contact"]
        : ["parse_invoice", "check_vendor_history", "check_domain", "compare_payment_account", "request_independent_verification"],
      evidence: [],
      risk_signals: [
        { signal_type: "ACCOUNT_CHANGED", severity: "CRITICAL", score_weight: 40, description: "Requested bank account differs from trusted account.", source_tool: "compare_payment_account" },
        { signal_type: "DOMAIN_MISMATCH", severity: "HIGH", score_weight: 30, description: "Sender domain conflicts with known domain 'acme.in'.", source_tool: "check_domain" },
        { signal_type: "VERIFICATION_UNAVAILABLE", severity: "HIGH", score_weight: 20, description: "Independent verification channel unavailable to resolve ambiguity.", source_tool: "request_independent_verification" },
        { signal_type: "UNUSUAL_AMOUNT", severity: "MEDIUM", score_weight: 15, description: "Invoice amount exceeds historical maximum.", source_tool: "check_vendor_history" },
        { signal_type: "URGENT_REQUEST", severity: "LOW", score_weight: 10, description: "Payment request flagged as urgent.", source_tool: "parse_invoice" },
      ],
      failures: [
        { tool_name: "request_independent_verification", category: "TOOL_UNAVAILABLE", detail: "Primary channel unavailable" }
      ],
      trace: [
        { phase: "OBSERVE", detail: `New payment request ${c.request_id} received` },
        { phase: "DECIDE", detail: "Extract and validate invoice metadata", tool: "parse_invoice" },
        { phase: "ACT", detail: "parse_invoice → SUCCESS", tool: "parse_invoice" },
        { phase: "EVALUATE", detail: "Payment request contains the required invoice metadata.", tool: "parse_invoice" },
        { phase: "DECIDE", detail: "Establish trusted vendor baseline", tool: "check_vendor_history" },
        { phase: "ACT", detail: "check_vendor_history → SUCCESS", tool: "check_vendor_history" },
        { phase: "EVALUATE", detail: "Vendor exists in the trusted registry.", tool: "check_vendor_history" },
        { phase: "DECIDE", detail: "Verify sender domain against known vendor domain", tool: "check_domain" },
        { phase: "ACT", detail: "check_domain → CONFLICT", tool: "check_domain" },
        { phase: "EVALUATE", detail: "Sender domain does not match the trusted vendor domain.", tool: "check_domain" },
        { phase: "DECIDE", detail: "Check for payment account changes", tool: "compare_payment_account" },
        { phase: "ACT", detail: "compare_payment_account → CONFLICT", tool: "compare_payment_account" },
        { phase: "EVALUATE", detail: "Requested payment account differs from the trusted account.", tool: "compare_payment_account" },
        { phase: "DECIDE", detail: "Risk signals detected — attempting independent verification", tool: "request_independent_verification" },
        { phase: "ACT", detail: "request_independent_verification → UNAVAILABLE", tool: "request_independent_verification" },
        { phase: "EVALUATE", detail: "Trusted independent verification channel is unavailable.", tool: "request_independent_verification" },
        { phase: "FAILURE", detail: "request_independent_verification failure detected (TOOL_UNAVAILABLE): Primary channel unreachable", tool: "request_independent_verification" },
        { phase: "ADAPT", detail: "Primary verification channel failed. Replanning alternative strategy: secondary trusted-contact verification." },
        { phase: "DECIDE", detail: "Attempt secondary out-of-band contact", tool: "verify_via_trusted_contact" },
        { phase: "ACT", detail: `verify_via_trusted_contact → ${isContactConfirmed ? "SUCCESS" : "UNAVAILABLE"}`, tool: "verify_via_trusted_contact" },
        { phase: "EVALUATE", detail: isContactConfirmed ? "Trusted contact confirmed change" : "Trusted contact was unreachable", tool: "verify_via_trusted_contact" },
        ...(isContactConfirmed ? [] : [{ phase: "FAILURE", detail: "verify_via_trusted_contact failure detected: Contact unreachable", tool: "verify_via_trusted_contact" }]),
        { phase: "ADAPT", detail: isContactConfirmed ? "Secondary verification succeeded; allowing approved change" : "All verification channels exhausted. Automatic approval prohibited." },
        { phase: "DECIDE", detail: "Evidence collection complete" },
        { phase: "FINAL", detail: `${finalAction}: ${reason}` },
      ],
    };
  }

  return (
    <div className="app-container">
      {/* 1. Header Bar */}
      <Header
        activeCaseId={activeCase?.request_id}
        isOnline={isOnline}
        isReplaying={isReplaying}
        viewMode={viewMode}
        benchmarkCount={benchmarkSummary?.total_cases || 52}
        onToggleViewMode={setViewMode}
        onRunInvestigation={() => executeInvestigation(activeCase, true)}
        onReplayTrace={handleReplayClick}
        onOpenRawModal={() => setIsRawModalOpen(true)}
        onOpenDemoVideoModal={() => setIsDemoVideoModalOpen(true)}
      />

      {viewMode === "benchmark" ? (
        /* M7 Benchmark & Evaluation View */
        <BenchmarkDashboard
          summary={benchmarkSummary}
          isLoading={isBenchmarkLoading}
          onRunBenchmark={handleTriggerBenchmark}
          onInspectCase={handleInspectBenchmarkCase}
        />
      ) : (
        <>
          {/* 2. Scenario Showcase (Top) */}
          <CaseSelector
            presets={presets}
            recentCases={recentCases}
            selectedCaseId={activeCase?.request_id}
            onSelectCase={(c) => executeInvestigation(c, true)}
          />

          {/* 3. Streamlined Two-Column Hero Command Center */}
          <div className="main-grid">
            {/* Left Column: The Invoice & Investigation Story */}
            <div className="column-stack">
              {/* Executive Digital Invoice Card */}
              <PaymentContext
                request={activeCase}
                riskSignals={investigation?.risk_signals || []}
              />

              {/* Agent Investigation Timeline (Story Mode & Technical OODA) */}
              <AgentTrace
                trace={investigation?.trace || []}
                visibleCount={visibleStepCount}
                isReplaying={isReplaying}
                adaptations={investigation?.adaptations || 0}
              />
            </div>

            {/* Right Column: The AI Verdict, Risk Gauge & Chaos Simulator */}
            <div className="column-stack">
              {/* Authoritative Policy Decision Report (Hero Position at Top Right!) */}
              <DecisionReport
                finalAction={investigation?.final_action || "HUMAN_REVIEW"}
                reason={investigation?.reason}
                riskSignals={investigation?.risk_signals || []}
              />

              {/* Deterministic Risk Meter & Security Findings */}
              <RiskPanel
                riskScore={investigation?.risk_score || 0}
                riskLevel={investigation?.risk_level || "LOW"}
                riskSignals={investigation?.risk_signals || []}
                evidenceItems={evidenceDetails.evidence_items || []}
                toolCalls={evidenceDetails.tool_calls || investigation?.evidence || []}
              />

              {/* Live Resilience & Outage Simulator */}
              <FailureInjectionBar
                verificationAvailable={verificationAvailable}
                onToggleVerification={() => {
                  const next = !verificationAvailable;
                  setVerificationAvailable(next);
                  executeInvestigation(activeCase, true, { verification_available: next });
                }}
                trustedContactState={trustedContactState}
                onChangeTrustedContactState={(state) => {
                  setTrustedContactState(state);
                  executeInvestigation(activeCase, true, { trustedContactState: state });
                }}
                enableSecondary={enableSecondary}
                onToggleSecondary={() => {
                  const next = !enableSecondary;
                  setEnableSecondary(next);
                  executeInvestigation(activeCase, true, { enable_secondary: next });
                }}
              />
            </div>
          </div>
        </>
      )}

      {/* Modal for Raw Email Testing */}
      <RawInputModal
        isOpen={isRawModalOpen}
        onClose={() => setIsRawModalOpen(false)}
        onSubmitRaw={handleRawSubmit}
      />

      {/* Modal for Interactive Demo Video Studio & Video Recording */}
      <DemoVideoModal
        isOpen={isDemoVideoModalOpen}
        onClose={() => setIsDemoVideoModalOpen(false)}
      />
    </div>
  );
}
