"""Tool registry — maps tool names to executable definitions.

Instead of hard-coding tool calls in the controller, the agent selects
tools from this registry.  Each tool entry knows:

- what the tool does (description)
- how to call it given the current investigation context

This decouples tool *selection* (planner) from tool *execution* (registry).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..models.schemas import PaymentRequest, ToolResult
from ..tools.account import compare_payment_account
from ..tools.domain import check_domain
from ..tools.invoice import parse_invoice
from ..tools.vendor import check_vendor_history
from ..tools.verification import request_independent_verification


@dataclass(frozen=True)
class ToolEntry:
    """A registered tool the agent can select and execute."""

    name: str
    description: str
    execute: Callable[..., ToolResult]


# ── Tool wrapper functions ──────────────────────────────────────────
#
# Each wrapper extracts the parameters it needs from the shared
# investigation context (request, evidence_map, extra kwargs).


def _run_parse_invoice(
    request: PaymentRequest,
    evidence_map: dict[str, ToolResult],
    **_ctx: Any,
) -> ToolResult:
    return parse_invoice(request)


def _run_check_vendor_history(
    request: PaymentRequest,
    evidence_map: dict[str, ToolResult],
    **_ctx: Any,
) -> ToolResult:
    return check_vendor_history(request)


def _run_check_domain(
    request: PaymentRequest,
    evidence_map: dict[str, ToolResult],
    **_ctx: Any,
) -> ToolResult:
    known_domain: str | None = None
    vendor_result = evidence_map.get("check_vendor_history")
    if vendor_result:
        known_domain = vendor_result.evidence.get("known_domain")
    return check_domain(request, known_domain)


def _run_compare_payment_account(
    request: PaymentRequest,
    evidence_map: dict[str, ToolResult],
    **_ctx: Any,
) -> ToolResult:
    known_account: str | None = None
    vendor_result = evidence_map.get("check_vendor_history")
    if vendor_result:
        known_account = vendor_result.evidence.get("known_account")
    return compare_payment_account(request, known_account)


def _run_request_independent_verification(
    request: PaymentRequest,
    evidence_map: dict[str, ToolResult],
    **ctx: Any,
) -> ToolResult:
    return request_independent_verification(
        available=ctx.get("verification_available", False),
        verified=ctx.get("verification_verified"),
    )


def _run_verify_via_trusted_contact(
    request: PaymentRequest,
    evidence_map: dict[str, ToolResult],
    **ctx: Any,
) -> ToolResult:
    from ..tools.contact import verify_via_trusted_contact

    trusted_contact: str | None = None
    vendor_result = evidence_map.get("check_vendor_history")
    if vendor_result:
        trusted_contact = vendor_result.evidence.get("trusted_contact")

    return verify_via_trusted_contact(
        vendor_name=request.vendor_name,
        trusted_contact=trusted_contact,
        contact_reachable=ctx.get("trusted_contact_reachable", False),
        contact_confirmed=ctx.get("trusted_contact_confirmed"),
    )


# ── Default registry ────────────────────────────────────────────────


def create_default_registry() -> dict[str, ToolEntry]:
    """Build the standard tool registry for payment investigations."""
    return {
        "parse_invoice": ToolEntry(
            name="parse_invoice",
            description="Extract and validate invoice metadata",
            execute=_run_parse_invoice,
        ),
        "check_vendor_history": ToolEntry(
            name="check_vendor_history",
            description="Check vendor against the trusted vendor registry",
            execute=_run_check_vendor_history,
        ),
        "check_domain": ToolEntry(
            name="check_domain",
            description="Compare sender domain against known vendor domain",
            execute=_run_check_domain,
        ),
        "compare_payment_account": ToolEntry(
            name="compare_payment_account",
            description="Detect payment account changes",
            execute=_run_compare_payment_account,
        ),
        "request_independent_verification": ToolEntry(
            name="request_independent_verification",
            description="Attempt verification through primary automated verification channel",
            execute=_run_request_independent_verification,
        ),
        "verify_via_trusted_contact": ToolEntry(
            name="verify_via_trusted_contact",
            description="Attempt secondary out-of-band verification via vendor's registered contact",
            execute=_run_verify_via_trusted_contact,
        ),
    }
