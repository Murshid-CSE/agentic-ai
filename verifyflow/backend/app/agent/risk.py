"""Deterministic risk signal extraction and scoring engine.

Security principle:
Risk is not an arbitrary number produced by an LLM prompt.
Instead:
    Evidence
        ↓
    Deterministic signals
        ↓
    Risk assessment & score
"""

from __future__ import annotations

from typing import Any

from ..models.schemas import (
    PaymentRequest,
    RiskAssessment,
    RiskLevel,
    RiskSignal,
    RiskSignalType,
    ToolResult,
    ToolStatus,
)

# Prototype risk weights
SIGNAL_WEIGHTS: dict[RiskSignalType, tuple[int, RiskLevel]] = {
    RiskSignalType.ACCOUNT_CHANGED: (40, RiskLevel.CRITICAL),
    RiskSignalType.UNKNOWN_VENDOR: (40, RiskLevel.CRITICAL),
    RiskSignalType.VERIFICATION_FAILED: (40, RiskLevel.CRITICAL),
    RiskSignalType.DOMAIN_MISMATCH: (30, RiskLevel.HIGH),
    RiskSignalType.VERIFICATION_UNAVAILABLE: (20, RiskLevel.HIGH),
    RiskSignalType.UNUSUAL_AMOUNT: (15, RiskLevel.MEDIUM),
    RiskSignalType.URGENT_REQUEST: (10, RiskLevel.LOW),
}


def compute_risk_level(score: int) -> RiskLevel:
    """Classify a 0-100 numerical risk score into an operational level."""
    if score <= 15:
        return RiskLevel.LOW
    if score <= 45:
        return RiskLevel.MEDIUM
    if score <= 75:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def extract_risk_signals(
    request: PaymentRequest,
    evidence_map: dict[str, ToolResult],
) -> RiskAssessment:
    """Analyze the payment request and accumulated evidence to extract risk signals.

    Parameters
    ----------
    request:
        The initial payment request.
    evidence_map:
        Mapping of tool name to ToolResult.

    Returns
    -------
    RiskAssessment
        Total score (0-100), risk level, and all detected risk signals.
    """
    signals: list[RiskSignal] = []

    vendor_res = evidence_map.get("check_vendor_history")
    domain_res = evidence_map.get("check_domain")
    account_res = evidence_map.get("compare_payment_account")
    verify_res = evidence_map.get("request_independent_verification")

    # 1. Unknown vendor check
    if vendor_res and (
        vendor_res.evidence.get("vendor_found") is False
        or vendor_res.status == ToolStatus.CONFLICT
    ):
        w, lev = SIGNAL_WEIGHTS[RiskSignalType.UNKNOWN_VENDOR]
        signals.append(
            RiskSignal(
                signal_type=RiskSignalType.UNKNOWN_VENDOR,
                severity=lev,
                confidence=vendor_res.confidence,
                score_weight=w,
                description=f"Vendor '{request.vendor_name}' not recognized in trusted registry.",
                source_tool="check_vendor_history",
            )
        )

    # 2. Domain mismatch check
    if domain_res and (
        domain_res.status == ToolStatus.CONFLICT
        or domain_res.evidence.get("match") is False
    ):
        w, lev = SIGNAL_WEIGHTS[RiskSignalType.DOMAIN_MISMATCH]
        known_dom = domain_res.evidence.get("known_domain", "unknown")
        signals.append(
            RiskSignal(
                signal_type=RiskSignalType.DOMAIN_MISMATCH,
                severity=lev,
                confidence=domain_res.confidence,
                score_weight=w,
                description=f"Sender domain '{request.sender_domain}' conflicts with known domain '{known_dom}'.",
                source_tool="check_domain",
            )
        )

    # 3. Account changed check
    if account_res and (
        account_res.evidence.get("changed") is True
        or account_res.status == ToolStatus.CONFLICT
    ):
        w, lev = SIGNAL_WEIGHTS[RiskSignalType.ACCOUNT_CHANGED]
        known_acc = account_res.evidence.get("known_account", "unknown")
        signals.append(
            RiskSignal(
                signal_type=RiskSignalType.ACCOUNT_CHANGED,
                severity=lev,
                confidence=account_res.confidence,
                score_weight=w,
                description=f"Requested bank account '{request.requested_account}' differs from trusted account '{known_acc}'.",
                source_tool="compare_payment_account",
            )
        )

    # 4. Unusual amount check (relative to vendor history)
    if vendor_res and vendor_res.evidence.get("vendor_found") is True:
        hist_max = vendor_res.evidence.get("historical_amount_max")
        if hist_max and request.amount > float(hist_max):
            w, lev = SIGNAL_WEIGHTS[RiskSignalType.UNUSUAL_AMOUNT]
            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.UNUSUAL_AMOUNT,
                    severity=lev,
                    confidence=0.95,
                    score_weight=w,
                    description=f"Invoice amount ({request.amount}) exceeds historical maximum ({hist_max}).",
                    source_tool="check_vendor_history",
                )
            )

    # 5. Urgent request flag
    if request.urgency and request.urgency.strip().lower() == "urgent":
        w, lev = SIGNAL_WEIGHTS[RiskSignalType.URGENT_REQUEST]
        signals.append(
            RiskSignal(
                signal_type=RiskSignalType.URGENT_REQUEST,
                severity=lev,
                confidence=0.90,
                score_weight=w,
                description="Payment request flagged as urgent, a common social-engineering pressure tactic.",
                source_tool="parse_invoice",
            )
        )

    # 6. Independent verification status
    if verify_res:
        if (
            verify_res.status == ToolStatus.CONFLICT
            or verify_res.evidence.get("verified") is False
        ):
            w, lev = SIGNAL_WEIGHTS[RiskSignalType.VERIFICATION_FAILED]
            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.VERIFICATION_FAILED,
                    severity=lev,
                    confidence=verify_res.confidence,
                    score_weight=w,
                    description="Out-of-band verification failed or repudiated by trusted contact.",
                    source_tool="request_independent_verification",
                )
            )
        elif (
            verify_res.status == ToolStatus.UNAVAILABLE
            or verify_res.evidence.get("verification_available") is False
        ):
            w, lev = SIGNAL_WEIGHTS[RiskSignalType.VERIFICATION_UNAVAILABLE]
            signals.append(
                RiskSignal(
                    signal_type=RiskSignalType.VERIFICATION_UNAVAILABLE,
                    severity=lev,
                    confidence=verify_res.confidence,
                    score_weight=w,
                    description="Independent verification channel unavailable to resolve ambiguity.",
                    source_tool="request_independent_verification",
                )
            )

    total_score = min(100, sum(s.score_weight for s in signals))
    level = compute_risk_level(total_score)

    return RiskAssessment(
        score=total_score,
        level=level,
        signals=signals,
    )
