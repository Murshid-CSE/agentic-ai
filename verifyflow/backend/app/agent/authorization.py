"""Explicit runtime authorization gate — the final security arbiter.

Security principle:
No LLM output, tool result, malformed document, timeout, or exception
can directly cause an unauthorized approval.

This gate runs AFTER the policy engine and enforces inviolable security
invariants as runtime code (never as Python `assert` statements, which can
be disabled in optimized execution).
"""

from __future__ import annotations

from typing import Any

from ..models.schemas import (
    FinalAction,
    PaymentRequest,
    RiskAssessment,
    RiskLevel,
    ToolResult,
    ToolStatus,
)


def authorize_action(
    tentative_action: FinalAction,
    tentative_reason: str,
    evidence_map: dict[str, ToolResult],
    request: PaymentRequest,
    risk_assessment: RiskAssessment | None = None,
) -> tuple[FinalAction, str]:
    """Inspect and enforce runtime security boundaries before final authorization.

    Parameters
    ----------
    tentative_action:
        The action proposed by the policy engine.
    tentative_reason:
        The explanation for the proposed action.
    evidence_map:
        Mapping of tool name to executed ToolResult.
    request:
        The original validated payment request.
    risk_assessment:
        Optional risk assessment and detected signals.

    Returns
    -------
    tuple[FinalAction, str]
        Guaranteed safe action and reason.
    """

    # ── Invariant 1: Non-positive or zero invoice amount cannot be approved ───
    if request.amount <= 0:
        return (
            FinalAction.HOLD,
            f"AUTHORIZATION GATE: Non-positive invoice amount (${request.amount}) "
            "fails validity check; approval prohibited.",
        )

    # ── Invariant 2: Active repudiation by trusted contact ────────────────────
    contact_res = evidence_map.get("verify_via_trusted_contact")
    if contact_res is not None and (
        contact_res.status == ToolStatus.CONFLICT
        or contact_res.evidence.get("repudiated") is True
    ):
        if tentative_action == FinalAction.APPROVE:
            return (
                FinalAction.HUMAN_REVIEW,
                "AUTHORIZATION GATE ENFORCED: Trusted contact actively repudiated "
                "payment request. Automated approval prohibited.",
            )

    # ── Invariant 3: Changed bank account + unverified identity ───────────────
    # Under NO circumstances may an unverified bank account swap be approved.
    account_res = evidence_map.get("compare_payment_account")
    account_changed = (
        account_res is not None
        and (
            account_res.evidence.get("changed") is True
            or account_res.status == ToolStatus.CONFLICT
        )
    )

    verify_res = evidence_map.get("request_independent_verification")

    primary_verified = (
        verify_res is not None
        and verify_res.status == ToolStatus.SUCCESS
        and verify_res.evidence.get("verified") is True
    )
    secondary_verified = (
        contact_res is not None
        and contact_res.status == ToolStatus.SUCCESS
        and contact_res.evidence.get("confirmed") is True
    )
    verified = primary_verified or secondary_verified

    if account_changed and not verified:
        if tentative_action == FinalAction.APPROVE:
            # Overrule invalid approval proposal
            return (
                FinalAction.HUMAN_REVIEW,
                "AUTHORIZATION GATE ENFORCED: Bank account changed without "
                "independent confirmation. Automated approval strictly prohibited.",
            )

    # ── Invariant 4: Domain mismatch / spoofing ───────────────────────────────
    domain_res = evidence_map.get("check_domain")
    domain_conflict = (
        domain_res is not None
        and (
            domain_res.status == ToolStatus.CONFLICT
            or domain_res.evidence.get("match") is False
        )
    )

    if domain_conflict and not verified:
        if tentative_action == FinalAction.APPROVE:
            return (
                FinalAction.HOLD,
                "AUTHORIZATION GATE ENFORCED: Sender domain conflicts with trusted "
                "vendor records. Automated approval prohibited.",
            )

    # ── Invariant 5: Unknown vendor fail-closed ───────────────────────────────
    vendor_res = evidence_map.get("check_vendor_history")
    vendor_known = (
        vendor_res is not None
        and vendor_res.evidence.get("vendor_found") is True
    )

    if not vendor_known:
        if tentative_action == FinalAction.APPROVE:
            return (
                FinalAction.HOLD,
                "AUTHORIZATION GATE ENFORCED: Vendor identity is unverified. "
                "Automated approval prohibited.",
            )

    # ── Invariant 6: Critical risk composite threshold ────────────────────────
    if risk_assessment and risk_assessment.level == RiskLevel.CRITICAL:
        if not verified and tentative_action == FinalAction.APPROVE:
            return (
                FinalAction.HUMAN_REVIEW,
                f"AUTHORIZATION GATE ENFORCED: Critical risk policy score "
                f"({risk_assessment.score}/100) requires human review.",
            )

    # ── Invariant 7: Default safe pass-through ────────────────────────────────
    return (tentative_action, tentative_reason)
