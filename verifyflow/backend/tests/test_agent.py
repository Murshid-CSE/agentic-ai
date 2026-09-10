"""Tests for the agent controller — validates the three demo scenarios
and the OBSERVE → DECIDE → ACT → EVALUATE → ADAPT reasoning loop.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.controller import run_investigation
from app.models.schemas import FinalAction, PaymentRequest


# ── Fixtures ─────────────────────────────────────────────────────────


def _make_request(**overrides) -> PaymentRequest:
    defaults = {
        "request_id": "TEST-001",
        "vendor_name": "Acme Supplies",
        "sender_email": "accounts@acme.in",
        "sender_domain": "acme.in",
        "invoice_number": "INV-1001",
        "amount": 42000,
        "requested_account": "BANK-ACME-001",
        "urgency": "normal",
    }
    defaults.update(overrides)
    return PaymentRequest(**defaults)


# ── Case A: Clean — APPROVE ──────────────────────────────────────────


def test_case_a_clean_approve():
    """Known vendor, known domain, known account → APPROVE."""
    request = _make_request()
    result = run_investigation(request)

    assert result.final_action == FinalAction.APPROVE
    assert result.adaptations == 0
    assert "parse_invoice" in result.tools_used
    assert "check_vendor_history" in result.tools_used
    assert "check_domain" in result.tools_used
    assert "compare_payment_account" in result.tools_used
    # Verification should NOT be called for a clean case
    assert "request_independent_verification" not in result.tools_used


# ── Case B: Suspicious — HUMAN_REVIEW ────────────────────────────────


def test_case_b_suspicious_human_review():
    """Known vendor, domain conflict, account changed, verification unavailable → HUMAN_REVIEW."""
    request = _make_request(
        request_id="VF-CASE-B",
        sender_email="billing@acme-payments.co",
        sender_domain="acme-payments.co",
        invoice_number="INV-4938",
        amount=125000,
        requested_account="BANK-ACME-999",
        urgency="urgent",
    )
    result = run_investigation(request, verification_available=False)

    assert result.final_action == FinalAction.HUMAN_REVIEW
    assert result.adaptations == 1
    assert "request_independent_verification" in result.tools_used


# ── Case C: Ambiguous — HUMAN_REVIEW ─────────────────────────────────


def test_case_c_ambiguous_human_review():
    """Known vendor, domain changed, account changed, verification unavailable → HUMAN_REVIEW."""
    request = _make_request(
        request_id="VF-CASE-C",
        vendor_name="Delta Components",
        sender_email="finance@delta-corp.com",
        sender_domain="delta-corp.com",
        invoice_number="INV-7721",
        amount=45000,
        requested_account="BANK-DELTA-NEW-099",
        urgency="normal",
    )
    result = run_investigation(request, verification_available=False)

    assert result.final_action == FinalAction.HUMAN_REVIEW
    assert result.adaptations == 1
    assert "request_independent_verification" in result.tools_used


# ── Case C variant: Verification succeeds → APPROVE ──────────────────


def test_case_c_with_verification_success():
    """Known vendor, domain changed, account changed, verification succeeds → APPROVE."""
    request = _make_request(
        request_id="VF-CASE-C-VERIFIED",
        vendor_name="Delta Components",
        sender_email="finance@delta-corp.com",
        sender_domain="delta-corp.com",
        invoice_number="INV-7721",
        amount=45000,
        requested_account="BANK-DELTA-NEW-099",
        urgency="normal",
    )
    result = run_investigation(
        request,
        verification_available=True,
        verification_verified=True,
    )

    assert result.final_action == FinalAction.APPROVE
    assert result.adaptations == 1
    assert "request_independent_verification" in result.tools_used


# ── Unknown vendor ───────────────────────────────────────────────────


def test_unknown_vendor_hold():
    """Unknown vendor → HOLD (no baseline to detect changes, default-deny)."""
    request = _make_request(
        vendor_name="Unknown Corp",
        sender_domain="unknown.com",
        requested_account="BANK-UNKNOWN-001",
    )
    result = run_investigation(request, verification_available=False)

    # No known account or domain to compare against, so policy
    # cannot detect "changes" — it correctly defaults to HOLD.
    assert result.final_action == FinalAction.HOLD
    assert result.adaptations == 0
    # Should stop early — only parse_invoice and check_vendor_history
    assert len(result.tools_used) == 2


# ── Domain conflict only (no account change) ─────────────────────────


def test_domain_conflict_only():
    """Known vendor, domain conflict, but account matches → HOLD."""
    request = _make_request(
        sender_domain="acme-fake.com",
    )
    result = run_investigation(request)

    assert result.final_action == FinalAction.HOLD
    assert result.adaptations == 1  # verification is adaptive
    assert "request_independent_verification" in result.tools_used


# ── Evidence trail completeness ──────────────────────────────────────


def test_evidence_trail_complete():
    """Every investigation must produce evidence from at least 4 tools."""
    request = _make_request()
    result = run_investigation(request)

    assert len(result.evidence) >= 4
    tool_names = [e.tool_name for e in result.evidence]
    assert "parse_invoice" in tool_names
    assert "check_vendor_history" in tool_names
    assert "check_domain" in tool_names
    assert "compare_payment_account" in tool_names


# ═══════════════════════════════════════════════════════════════════
# NEW: Milestone 2 — Trace and dynamic behavior tests
# ═══════════════════════════════════════════════════════════════════


def test_trace_exists():
    """Every investigation must produce a non-empty reasoning trace."""
    result = run_investigation(_make_request())
    assert len(result.trace) > 0


def test_trace_starts_with_observe():
    """The trace must begin with an OBSERVE phase."""
    result = run_investigation(_make_request())
    assert result.trace[0].phase == "OBSERVE"


def test_trace_ends_with_final():
    """The trace must end with a FINAL phase."""
    result = run_investigation(_make_request())
    assert result.trace[-1].phase == "FINAL"


def test_trace_contains_decide_act_evaluate():
    """The trace must contain DECIDE, ACT, and EVALUATE phases."""
    result = run_investigation(_make_request())
    phases = {e.phase for e in result.trace}
    assert "DECIDE" in phases
    assert "ACT" in phases
    assert "EVALUATE" in phases


def test_trace_records_tool_names():
    """ACT entries in the trace must record the tool name."""
    result = run_investigation(_make_request())
    act_entries = [e for e in result.trace if e.phase == "ACT"]
    assert all(e.tool is not None for e in act_entries)


def test_clean_case_no_adapt_in_trace():
    """Clean case should have no ADAPT entries in the trace."""
    result = run_investigation(_make_request())
    adapt_entries = [e for e in result.trace if e.phase == "ADAPT"]
    assert len(adapt_entries) == 0


def test_suspicious_case_has_adapt_in_trace():
    """Suspicious case should have ADAPT entries in the trace."""
    request = _make_request(
        sender_domain="acme-payments.co",
        requested_account="BANK-ACME-999",
    )
    result = run_investigation(request, verification_available=False)
    adapt_entries = [e for e in result.trace if e.phase == "ADAPT"]
    assert len(adapt_entries) >= 1


def test_dynamic_tool_count_clean_vs_risky():
    """Clean case uses fewer tools than risky case."""
    clean = run_investigation(_make_request())
    risky = run_investigation(
        _make_request(
            sender_domain="acme-payments.co",
            requested_account="BANK-ACME-999",
        ),
        verification_available=False,
    )
    assert len(clean.tools_used) < len(risky.tools_used)


def test_unknown_vendor_early_stop():
    """Unknown vendor should stop after 2 tools (parse + vendor check)."""
    request = _make_request(
        vendor_name="Phantom LLC",
        sender_domain="phantom.com",
        requested_account="BANK-PHANTOM-001",
    )
    result = run_investigation(request)
    assert result.tools_used == ["parse_invoice", "check_vendor_history"]


def test_trace_is_chronological():
    """Trace entries must have monotonically non-decreasing timestamps."""
    result = run_investigation(_make_request())
    timestamps = [e.timestamp for e in result.trace]
    assert timestamps == sorted(timestamps)
