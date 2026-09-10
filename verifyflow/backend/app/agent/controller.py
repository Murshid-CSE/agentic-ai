"""Agent controller — the Observe → Decide → Act → Evaluate → Adapt loop.

This is the core of VerifyFlow's agentic behavior.  Instead of a fixed
tool sequence, the controller runs an adaptive reasoning loop:

    1. OBSERVE   — examine what we know so far
    2. DECIDE    — ask the planner which tool to run next (or stop)
    3. ACT       — execute the selected tool via the registry
    4. EVALUATE  — assess the result and update evidence
    5. FAILURE   — explicitly recognize and classify runtime failures
    6. ADAPT     — replan alternative action or safe escalation

Milestone 6 additions:
    - Explicit failure states (TOOL_UNAVAILABLE, INVALID_RESULT, etc.)
    - Controllable failure injection switches for demonstrations
    - Multi-step adaptation: replanning to secondary trusted contact upon primary verification failure
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..database.db import save_investigation
from ..models.schemas import (
    FinalAction,
    InvestigationResult,
    PaymentRequest,
    ToolResult,
    ToolStatus,
    TraceEntry,
)
from .authorization import authorize_action
from .failures import FailureCategory, FailureInjectionConfig, FailureRecord
from .planner import select_next_tool
from .policy import evaluate_policy
from .registry import create_default_registry
from .risk import extract_risk_signals
from .states import AgentPhase

# Safety limit — prevents runaway loops. With 6 tools this is generous.
MAX_ITERATIONS = 12


def run_investigation(
    request: PaymentRequest,
    *,
    verification_available: bool = False,
    verification_verified: bool | None = None,
    enable_secondary_verification: bool = False,
    trusted_contact_reachable: bool = False,
    trusted_contact_confirmed: bool | None = None,
    failure_injection: FailureInjectionConfig | None = None,
    persist: bool = True,
    db_path: Path | str | None = None,
) -> InvestigationResult:
    """Run a complete payment-change investigation with failure recovery.

    Parameters
    ----------
    request:
        The incoming payment request to investigate.
    verification_available:
        Whether primary automated verification can be reached.
    verification_verified:
        If primary verification is available, whether it confirmed the request.
    enable_secondary_verification:
        Whether to attempt multi-step adaptation via secondary trusted contact.
    trusted_contact_reachable:
        Whether the secondary trusted contact is reachable.
    trusted_contact_confirmed:
        Whether the secondary trusted contact confirmed the change.
    failure_injection:
        Controlled failure injection switches for testing and demo.
    persist:
        Whether to record the full case ledger in SQLite.
    db_path:
        Optional custom database path (e.g. for isolated testing).

    Returns
    -------
    InvestigationResult
        The final action with full evidence trail, reasoning trace,
        failure records, and deterministic risk assessment.
    """

    # ── Apply failure injection overrides ───────────────────────────

    ver_avail = verification_available
    tc_reachable = trusted_contact_reachable

    if failure_injection:
        if failure_injection.verification_service_offline:
            ver_avail = False
        if failure_injection.trusted_contact_unreachable:
            tc_reachable = False

    # ── Initialise investigation state ──────────────────────────────

    registry = create_default_registry()
    context = {
        "verification_available": ver_avail,
        "verification_verified": verification_verified,
        "trusted_contact_reachable": tc_reachable,
        "trusted_contact_confirmed": trusted_contact_confirmed,
    }

    evidence: list[ToolResult] = []
    evidence_map: dict[str, ToolResult] = {}
    tools_used: list[str] = []
    trace: list[TraceEntry] = []
    failures: list[dict[str, Any]] = []
    adaptations = 0
    phase = AgentPhase.RECEIVED

    def _trace(p: str, detail: str, *, tool: str | None = None) -> None:
        trace.append(TraceEntry(phase=p, detail=detail, tool=tool))

    # ── RECEIVED → OBSERVING ────────────────────────────────────────

    _trace("OBSERVE", f"New payment request {request.request_id} received")
    phase = AgentPhase.OBSERVING

    # ── Main reasoning loop ─────────────────────────────────────────

    iterations = 0

    while iterations < MAX_ITERATIONS:
        iterations += 1

        # ── DECIDE ──────────────────────────────────────────────────
        phase = AgentPhase.DECIDING

        selection = select_next_tool(
            evidence_map,
            set(tools_used),
            enable_secondary_verification=enable_secondary_verification,
        )

        if selection is None:
            _trace("DECIDE", "Evidence collection complete")
            break

        tool_name, reason, is_adaptive = selection
        _trace("DECIDE", reason, tool=tool_name)

        # ── CYCLE DETECTION (Defense against infinite loops) ──────────
        if tools_used.count(tool_name) >= 2:
            _trace(
                "FAILURE",
                f"Cycle detected: {tool_name} already executed {tools_used.count(tool_name)} times; aborting loop.",
                tool=tool_name,
            )
            failures.append({
                "tool_name": tool_name,
                "category": FailureCategory.TIMEOUT.value,
                "detail": f"Cycle detection limit reached for tool {tool_name}",
            })
            break

        # ── ACT ─────────────────────────────────────────────────────
        phase = AgentPhase.ACTING

        tool_entry = registry[tool_name]
        try:
            result = tool_entry.execute(request, evidence_map, **context)
        except Exception as exc:
            # Trap unexpected tool exceptions — never crash or compromise authorization
            result = ToolResult(
                tool_name=tool_name,
                status=ToolStatus.FAILED,
                summary=f"Tool execution exception: {exc}",
                confidence=0.0,
                evidence={"error": str(exc)},
            )

        evidence.append(result)
        evidence_map[tool_name] = result
        tools_used.append(tool_name)

        _trace("ACT", f"{tool_name} → {result.status.value}", tool=tool_name)

        # ── EVALUATE ────────────────────────────────────────────────
        phase = AgentPhase.EVALUATING
        _trace("EVALUATE", result.summary, tool=tool_name)

        # ── FAILURE DETECTION & CLASSIFICATION ──────────────────────
        is_tool_failure = result.status in (ToolStatus.UNAVAILABLE, ToolStatus.FAILED)
        if is_tool_failure:
            phase = AgentPhase.FAILURE
            cat = (
                FailureCategory.TOOL_UNAVAILABLE.value
                if result.status == ToolStatus.UNAVAILABLE
                else FailureCategory.INVALID_RESULT.value
            )
            failure_rec = {
                "tool_name": tool_name,
                "category": cat,
                "detail": result.summary,
            }
            failures.append(failure_rec)
            _trace(
                "FAILURE",
                f"{tool_name} failure detected ({cat}): {result.summary}",
                tool=tool_name,
            )

        # ── ADAPT (if this was a risk-driven tool selection or replanning) ─

        if is_adaptive:
            adaptations += 1
            phase = AgentPhase.ADAPTING
            if tool_name == "verify_via_trusted_contact":
                _trace(
                    "ADAPT",
                    "Primary verification channel failed. Replanning alternative strategy: secondary trusted-contact verification.",
                )
            elif tool_name == "request_independent_verification":
                _trace("ADAPT", "Risk signals detected. Shifting strategy to independent verification.")
            else:
                _trace("ADAPT", "Risk-driven investigation step completed.")

    # ── RISK ASSESSMENT, POLICY ENGINE & AUTHORIZATION GATE ─────────

    risk_assessment = extract_risk_signals(request, evidence_map)
    tentative_action, tentative_reason = evaluate_policy(evidence_map, risk_assessment)

    # Inviolable runtime authorization gate
    final_action, reason = authorize_action(
        tentative_action=tentative_action,
        tentative_reason=tentative_reason,
        evidence_map=evidence_map,
        request=request,
        risk_assessment=risk_assessment,
    )

    phase = AgentPhase.COMPLETED
    _trace(
        "FINAL",
        f"{final_action.value}: {reason} "
        f"[Risk Score: {risk_assessment.score}/100 ({risk_assessment.level.value})]",
    )

    investigation_result = InvestigationResult(
        request_id=request.request_id,
        final_action=final_action,
        reason=reason,
        tools_used=tools_used,
        adaptations=adaptations,
        evidence=evidence,
        trace=trace,
        risk_score=risk_assessment.score,
        risk_level=risk_assessment.level,
        risk_signals=risk_assessment.signals,
        failures=failures,
    )

    # ── PERSISTENCE (SQLite Evidence Ledger) ────────────────────────

    if persist:
        save_investigation(request, investigation_result, db_path=db_path)

    return investigation_result
