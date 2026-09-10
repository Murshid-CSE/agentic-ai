"""Deterministic planner — decides which tool to run next.

This is the agent's decision engine.  It examines collected evidence
and selects the most useful next tool, or returns ``None`` to signal
that evidence collection is complete.

The planner operates in four phases:

    Phase 1  Extract invoice metadata            (baseline)
    Phase 2  Establish vendor identity            (baseline)
    Phase 3  Verify identity signals              (standard checks)
    Phase 4  Risk-driven independent verification (adaptive)

Phase 4 tools are only selected when earlier phases surfaced a risk
signal (domain conflict, account change).  These selections are
marked ``is_adaptive=True`` so the controller can count adaptations.

**Milestone 2 design choice:** the planner is fully deterministic.
Milestone 4 will optionally let an LLM influence tool selection.
"""

from __future__ import annotations

from typing import NamedTuple

from ..models.schemas import ToolResult, ToolStatus


class ToolSelection(NamedTuple):
    """A planner decision to run a specific tool."""

    tool_name: str
    reason: str
    is_adaptive: bool


def select_next_tool(
    evidence_map: dict[str, ToolResult],
    used_tools: set[str],
    *,
    enable_secondary_verification: bool = False,
) -> ToolSelection | None:
    """Choose the next investigation tool based on current evidence.

    Parameters
    ----------
    evidence_map:
        Tool name → result for all tools executed so far.
    used_tools:
        Set of tool names already executed.
    enable_secondary_verification:
        Whether to attempt secondary trusted-contact verification upon failure.

    Returns
    -------
    ToolSelection | None
        The next tool to run with a reason, or ``None`` if evidence
        collection is complete.
    """

    # ── Phase 1: Extract invoice metadata ───────────────────────────
    if "parse_invoice" not in used_tools:
        return ToolSelection(
            tool_name="parse_invoice",
            reason="Extract and validate invoice metadata",
            is_adaptive=False,
        )

    # ── Phase 2: Establish vendor baseline ──────────────────────────
    if "check_vendor_history" not in used_tools:
        return ToolSelection(
            tool_name="check_vendor_history",
            reason="Establish trusted vendor baseline",
            is_adaptive=False,
        )

    vendor_result = evidence_map.get("check_vendor_history")
    vendor_known = (
        vendor_result is not None
        and vendor_result.evidence.get("vendor_found") is True
    )

    if not vendor_known:
        # Unknown vendor — no baseline for domain/account comparison.
        # Evidence collection is complete; policy engine will decide.
        return None

    # ── Phase 3: Verify identity signals ────────────────────────────
    if "check_domain" not in used_tools:
        return ToolSelection(
            tool_name="check_domain",
            reason="Verify sender domain against known vendor domain",
            is_adaptive=False,
        )

    if "compare_payment_account" not in used_tools:
        return ToolSelection(
            tool_name="compare_payment_account",
            reason="Check for payment account changes",
            is_adaptive=False,
        )

    # ── Phase 4: Risk-driven adaptation & replanning ────────────────
    domain_result = evidence_map.get("check_domain")
    account_result = evidence_map.get("compare_payment_account")

    domain_conflict = (
        domain_result is not None
        and domain_result.status == ToolStatus.CONFLICT
    )
    account_changed = (
        account_result is not None
        and account_result.evidence.get("changed") is True
    )

    if domain_conflict or account_changed:
        # Step 4a: Primary independent verification
        if "request_independent_verification" not in used_tools:
            return ToolSelection(
                tool_name="request_independent_verification",
                reason="Risk signals detected — attempting independent verification",
                is_adaptive=True,
            )

        # Step 4b: If primary verification failed, replan to secondary contact
        if enable_secondary_verification:
            primary_ver = evidence_map.get("request_independent_verification")
            if (
                primary_ver is not None
                and primary_ver.status in (ToolStatus.UNAVAILABLE, ToolStatus.FAILED)
                and "verify_via_trusted_contact" not in used_tools
            ):
                return ToolSelection(
                    tool_name="verify_via_trusted_contact",
                    reason="Primary verification failed — replanning alternative strategy: out-of-band trusted contact verification",
                    is_adaptive=True,
                )

    # ── Evidence collection complete ────────────────────────────────
    return None
