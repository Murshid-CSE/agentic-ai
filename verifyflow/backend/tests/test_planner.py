"""Tests for the deterministic planner — verifies dynamic tool selection."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.planner import select_next_tool
from app.models.schemas import ToolResult, ToolStatus


# ── Helpers ──────────────────────────────────────────────────────────


def _vendor_found() -> ToolResult:
    return ToolResult(
        tool_name="check_vendor_history",
        status=ToolStatus.SUCCESS,
        summary="Vendor exists.",
        evidence={
            "vendor_found": True,
            "known_domain": "acme.in",
            "known_account": "BANK-ACME-001",
        },
    )


def _vendor_not_found() -> ToolResult:
    return ToolResult(
        tool_name="check_vendor_history",
        status=ToolStatus.CONFLICT,
        summary="Vendor not found.",
        evidence={"vendor_found": False, "vendor": "Unknown Corp"},
    )


def _domain_match() -> ToolResult:
    return ToolResult(
        tool_name="check_domain",
        status=ToolStatus.SUCCESS,
        summary="Domain matches.",
        evidence={"match": True},
    )


def _domain_conflict() -> ToolResult:
    return ToolResult(
        tool_name="check_domain",
        status=ToolStatus.CONFLICT,
        summary="Domain conflict.",
        evidence={"match": False},
    )


def _account_match() -> ToolResult:
    return ToolResult(
        tool_name="compare_payment_account",
        status=ToolStatus.SUCCESS,
        summary="Account matches.",
        evidence={"changed": False},
    )


def _account_changed() -> ToolResult:
    return ToolResult(
        tool_name="compare_payment_account",
        status=ToolStatus.CONFLICT,
        summary="Account changed.",
        evidence={"changed": True},
    )


def _invoice_ok() -> ToolResult:
    return ToolResult(
        tool_name="parse_invoice",
        status=ToolStatus.SUCCESS,
        summary="Invoice OK.",
        evidence={"invoice_number": "INV-1001"},
    )


# ── Phase 1: First tool is always parse_invoice ─────────────────────


def test_first_tool_is_parse_invoice():
    sel = select_next_tool({}, set())
    assert sel is not None
    assert sel.tool_name == "parse_invoice"
    assert sel.is_adaptive is False


# ── Phase 2: Then vendor history ─────────────────────────────────────


def test_second_tool_is_vendor_history():
    evidence = {"parse_invoice": _invoice_ok()}
    sel = select_next_tool(evidence, {"parse_invoice"})
    assert sel is not None
    assert sel.tool_name == "check_vendor_history"
    assert sel.is_adaptive is False


# ── Unknown vendor stops early ───────────────────────────────────────


def test_unknown_vendor_stops_early():
    """If vendor is unknown, no point checking domain/account."""
    evidence = {
        "parse_invoice": _invoice_ok(),
        "check_vendor_history": _vendor_not_found(),
    }
    sel = select_next_tool(evidence, {"parse_invoice", "check_vendor_history"})
    assert sel is None


# ── Phase 3: Known vendor → check domain then account ────────────────


def test_known_vendor_check_domain():
    evidence = {
        "parse_invoice": _invoice_ok(),
        "check_vendor_history": _vendor_found(),
    }
    sel = select_next_tool(evidence, {"parse_invoice", "check_vendor_history"})
    assert sel is not None
    assert sel.tool_name == "check_domain"
    assert sel.is_adaptive is False


def test_known_vendor_check_account_after_domain():
    evidence = {
        "parse_invoice": _invoice_ok(),
        "check_vendor_history": _vendor_found(),
        "check_domain": _domain_match(),
    }
    used = {"parse_invoice", "check_vendor_history", "check_domain"}
    sel = select_next_tool(evidence, used)
    assert sel is not None
    assert sel.tool_name == "compare_payment_account"
    assert sel.is_adaptive is False


# ── Clean case stops without verification ────────────────────────────


def test_clean_case_no_verification():
    """All checks pass → no need for independent verification."""
    evidence = {
        "parse_invoice": _invoice_ok(),
        "check_vendor_history": _vendor_found(),
        "check_domain": _domain_match(),
        "compare_payment_account": _account_match(),
    }
    used = {
        "parse_invoice",
        "check_vendor_history",
        "check_domain",
        "compare_payment_account",
    }
    sel = select_next_tool(evidence, used)
    assert sel is None  # Done — no verification needed


# ── Phase 4: Risk signals trigger adaptive verification ──────────────


def test_domain_conflict_triggers_verification():
    evidence = {
        "parse_invoice": _invoice_ok(),
        "check_vendor_history": _vendor_found(),
        "check_domain": _domain_conflict(),
        "compare_payment_account": _account_match(),
    }
    used = {
        "parse_invoice",
        "check_vendor_history",
        "check_domain",
        "compare_payment_account",
    }
    sel = select_next_tool(evidence, used)
    assert sel is not None
    assert sel.tool_name == "request_independent_verification"
    assert sel.is_adaptive is True


def test_account_changed_triggers_verification():
    evidence = {
        "parse_invoice": _invoice_ok(),
        "check_vendor_history": _vendor_found(),
        "check_domain": _domain_match(),
        "compare_payment_account": _account_changed(),
    }
    used = {
        "parse_invoice",
        "check_vendor_history",
        "check_domain",
        "compare_payment_account",
    }
    sel = select_next_tool(evidence, used)
    assert sel is not None
    assert sel.tool_name == "request_independent_verification"
    assert sel.is_adaptive is True


def test_both_conflicts_trigger_verification():
    evidence = {
        "parse_invoice": _invoice_ok(),
        "check_vendor_history": _vendor_found(),
        "check_domain": _domain_conflict(),
        "compare_payment_account": _account_changed(),
    }
    used = {
        "parse_invoice",
        "check_vendor_history",
        "check_domain",
        "compare_payment_account",
    }
    sel = select_next_tool(evidence, used)
    assert sel is not None
    assert sel.tool_name == "request_independent_verification"
    assert sel.is_adaptive is True


# ── After verification, no more tools ────────────────────────────────


def test_stops_after_verification():
    """Once verification is done, evidence collection is complete."""
    evidence = {
        "parse_invoice": _invoice_ok(),
        "check_vendor_history": _vendor_found(),
        "check_domain": _domain_conflict(),
        "compare_payment_account": _account_changed(),
        "request_independent_verification": ToolResult(
            tool_name="request_independent_verification",
            status=ToolStatus.UNAVAILABLE,
            summary="Unavailable.",
            evidence={"verification_available": False},
        ),
    }
    used = {
        "parse_invoice",
        "check_vendor_history",
        "check_domain",
        "compare_payment_account",
        "request_independent_verification",
    }
    sel = select_next_tool(evidence, used)
    assert sel is None


# ── Dynamic stopping: different paths, different tool counts ─────────


def test_clean_path_uses_four_tools():
    """Clean case: parse → vendor → domain → account → done (4 tools)."""
    evidence: dict[str, ToolResult] = {}
    used: set[str] = set()
    tool_count = 0

    while True:
        sel = select_next_tool(evidence, used)
        if sel is None:
            break
        tool_count += 1
        used.add(sel.tool_name)
        # Simulate clean results
        if sel.tool_name == "parse_invoice":
            evidence[sel.tool_name] = _invoice_ok()
        elif sel.tool_name == "check_vendor_history":
            evidence[sel.tool_name] = _vendor_found()
        elif sel.tool_name == "check_domain":
            evidence[sel.tool_name] = _domain_match()
        elif sel.tool_name == "compare_payment_account":
            evidence[sel.tool_name] = _account_match()

    assert tool_count == 4


def test_risky_path_uses_five_tools():
    """Risky case: parse → vendor → domain → account → verify → done (5 tools)."""
    evidence: dict[str, ToolResult] = {}
    used: set[str] = set()
    tool_count = 0
    adaptive_count = 0

    while True:
        sel = select_next_tool(evidence, used)
        if sel is None:
            break
        tool_count += 1
        if sel.is_adaptive:
            adaptive_count += 1
        used.add(sel.tool_name)
        # Simulate risky results
        if sel.tool_name == "parse_invoice":
            evidence[sel.tool_name] = _invoice_ok()
        elif sel.tool_name == "check_vendor_history":
            evidence[sel.tool_name] = _vendor_found()
        elif sel.tool_name == "check_domain":
            evidence[sel.tool_name] = _domain_conflict()
        elif sel.tool_name == "compare_payment_account":
            evidence[sel.tool_name] = _account_changed()
        elif sel.tool_name == "request_independent_verification":
            evidence[sel.tool_name] = ToolResult(
                tool_name="request_independent_verification",
                status=ToolStatus.UNAVAILABLE,
                summary="Unavailable.",
                evidence={"verification_available": False},
            )

    assert tool_count == 5
    assert adaptive_count == 1


def test_unknown_vendor_path_uses_two_tools():
    """Unknown vendor: parse → vendor → done (2 tools, no domain/account)."""
    evidence: dict[str, ToolResult] = {}
    used: set[str] = set()
    tool_count = 0

    while True:
        sel = select_next_tool(evidence, used)
        if sel is None:
            break
        tool_count += 1
        used.add(sel.tool_name)
        if sel.tool_name == "parse_invoice":
            evidence[sel.tool_name] = _invoice_ok()
        elif sel.tool_name == "check_vendor_history":
            evidence[sel.tool_name] = _vendor_not_found()

    assert tool_count == 2
