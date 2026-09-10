"""Deterministic policy engine — the security boundary.

Security principle:
The LLM does NOT control authorization. This module evaluates structured
evidence and risk signals, enforcing deterministic policy boundaries:

1. APPROVE requires:
   - Known trusted vendor
   - Matched sender domain
   - Unchanged bank account OR bank account change verified out-of-band

2. APPROVE is STRICTLY PROHIBITED if:
   - Bank account changed AND identity not independently verified

3. Default-deny:
   - Any inconclusive, conflicting, or unverified evidence results
     in HOLD or HUMAN_REVIEW.
"""

from __future__ import annotations

from ..models.schemas import (
    FinalAction,
    RiskAssessment,
    RiskSignalType,
    ToolResult,
    ToolStatus,
)


def evaluate_policy(
    evidence_map: dict[str, ToolResult],
    risk_assessment: RiskAssessment | None = None,
) -> tuple[FinalAction, str]:
    """Evaluate collected evidence and risk signals against the security policy.

    Parameters
    ----------
    evidence_map:
        Mapping of tool name → ToolResult for all tools executed.
    risk_assessment:
        Optional deterministic risk assessment and detected signals.

    Returns
    -------
    tuple[FinalAction, str]
        (action, reason) — guaranteed non-empty deterministic decision.
    """

    vendor_result = evidence_map.get("check_vendor_history")
    domain_result = evidence_map.get("check_domain")
    account_result = evidence_map.get("compare_payment_account")
    verification_result = evidence_map.get("request_independent_verification")
    contact_result = evidence_map.get("verify_via_trusted_contact")

    # ── Signal extraction ───────────────────────────────────────────

    vendor_known = (
        vendor_result is not None
        and vendor_result.evidence.get("vendor_found") is True
    )

    domain_conflict = (
        domain_result is not None
        and (
            domain_result.status == ToolStatus.CONFLICT
            or domain_result.evidence.get("match") is False
        )
    )

    account_changed = (
        account_result is not None
        and (
            account_result.evidence.get("changed") is True
            or account_result.status == ToolStatus.CONFLICT
        )
    )

    primary_verified = (
        verification_result is not None
        and verification_result.status == ToolStatus.SUCCESS
        and verification_result.evidence.get("verified") is True
    )

    secondary_verified = (
        contact_result is not None
        and contact_result.status == ToolStatus.SUCCESS
        and contact_result.evidence.get("confirmed") is True
    )

    verified = primary_verified or secondary_verified
    verification_attempted = (verification_result is not None) or (contact_result is not None)

    # ── Strict Boundary: Account changed ─────────────────────────────

    if account_changed:
        if verified:
            # Verified through trusted contact channel
            return (
                FinalAction.APPROVE,
                "Payment account changed but independently verified "
                "through a trusted channel.",
            )

        # Repudiated by trusted contact
        if contact_result is not None and contact_result.status == ToolStatus.CONFLICT:
            return (
                FinalAction.HUMAN_REVIEW,
                "Payment account changed and trusted contact actively repudiated the update request.",
            )

        # APPROVAL STRICTLY PROHIBITED
        if verification_attempted:
            return (
                FinalAction.HUMAN_REVIEW,
                "Payment account changed and independent verification "
                "did not confirm the request.",
            )

        return (
            FinalAction.HOLD,
            "Payment account changed; verification required.",
        )

    # ── Domain conflict (impersonation / lookalike risk) ─────────────

    if domain_conflict:
        return (
            FinalAction.HOLD,
            "Sender domain conflicts with the trusted vendor domain.",
        )

    # ── Unknown vendor ───────────────────────────────────────────────

    if not vendor_known:
        return (
            FinalAction.HOLD,
            "Vendor is unknown or unverified; approval prohibited.",
        )

    # ── Clean path: Known vendor + domain match + account match ──────

    if (
        vendor_known
        and not domain_conflict
        and account_result is not None
        and account_result.status == ToolStatus.SUCCESS
    ):
        return (
            FinalAction.APPROVE,
            "Vendor, sender domain, and payment account match "
            "trusted records.",
        )

    # ── Default-deny fallback ────────────────────────────────────────

    return (
        FinalAction.HOLD,
        "Evidence is insufficient for automatic approval.",
    )
