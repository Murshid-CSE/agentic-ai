"""Tests for Milestone 6: Failure Recognition, Multi-Step Adaptation & Recovery."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.controller import run_investigation
from app.agent.failures import FailureCategory, FailureInjectionConfig
from app.database.db import get_case_trace
from app.models.schemas import FinalAction, PaymentRequest, ToolStatus
from app.tools.contact import verify_via_trusted_contact


def _make_hero_request(**overrides) -> PaymentRequest:
    defaults = {
        "request_id": "VF-FAIL-HERO",
        "vendor_name": "Acme Supplies",
        "sender_email": "billing@acme-payments.co",
        "sender_domain": "acme-payments.co",
        "invoice_number": "INV-4938",
        "amount": 125000,
        "requested_account": "BANK-ACME-999",
        "urgency": "urgent",
    }
    defaults.update(overrides)
    return PaymentRequest(**defaults)


# ── Test 1: Tool succeeds → no adaptation ────────────────────────────


def test_tool_succeeds_no_adaptation():
    """Clean request: all tools succeed without failure or adaptation."""
    req = PaymentRequest(
        request_id="VF-CLEAN",
        vendor_name="Acme Supplies",
        sender_email="accounts@acme.in",
        sender_domain="acme.in",
        invoice_number="INV-1001",
        amount=42000,
        requested_account="BANK-ACME-001",
        urgency="normal",
    )
    result = run_investigation(req, persist=False)
    assert result.final_action == FinalAction.APPROVE
    assert result.adaptations == 0
    assert len(result.failures) == 0
    assert not any(e.phase == "FAILURE" for e in result.trace)


# ── Test 2: Tool unavailable → failure recognition & adaptation ──────


def test_primary_tool_unavailable_triggers_failure_and_adaptation():
    """Primary verification unavailable → FAILURE recognized in trace, adapts to escalation."""
    req = _make_hero_request()
    result = run_investigation(req, verification_available=False, persist=False)

    assert result.final_action == FinalAction.HUMAN_REVIEW
    assert result.adaptations == 1
    assert len(result.failures) == 1
    assert result.failures[0]["category"] == FailureCategory.TOOL_UNAVAILABLE.value
    assert any(e.phase == "FAILURE" for e in result.trace)


# ── Test 3: Multi-step adaptation: secondary contact succeeds → APPROVE ─


def test_multi_step_adaptation_secondary_contact_succeeds():
    """Multi-step recovery:
    Primary verification fails (UNAVAILABLE)
    → Agent recognizes FAILURE
    → Replans (ADAPT)
    → Attempts secondary trusted contact verification
    → Contact confirms
    → Agent adapts decision to APPROVE!
    """
    req = _make_hero_request(request_id="VF-RECOVER-SUCCESS")
    result = run_investigation(
        req,
        verification_available=False,
        enable_secondary_verification=True,
        trusted_contact_reachable=True,
        trusted_contact_confirmed=True,
        persist=False,
    )

    assert result.final_action == FinalAction.APPROVE
    assert result.adaptations == 2
    assert "verify_via_trusted_contact" in result.tools_used
    assert len(result.tools_used) == 6

    # Verify trace sequence
    phases = [e.phase for e in result.trace]
    assert "FAILURE" in phases
    assert phases.count("ADAPT") >= 2


# ── Test 4: Multi-step adaptation: secondary contact fails → HUMAN_REVIEW


def test_multi_step_adaptation_secondary_contact_fails_human_review():
    """Controlled failure chain:
    Primary verification fails (UNAVAILABLE)
    → Agent replans to secondary trusted contact
    → Secondary contact is also unreachable (FAILURE)
    → Agent adapts to safe escalation (HUMAN_REVIEW).
    """
    req = _make_hero_request(request_id="VF-CHAIN-FAIL")
    result = run_investigation(
        req,
        verification_available=False,
        enable_secondary_verification=True,
        trusted_contact_reachable=False,
        persist=False,
    )

    assert result.final_action == FinalAction.HUMAN_REVIEW
    assert result.adaptations == 2
    assert len(result.tools_used) == 6
    assert len(result.failures) == 2
    failure_tools = [f["tool_name"] for f in result.failures]
    assert "request_independent_verification" in failure_tools
    assert "verify_via_trusted_contact" in failure_tools


# ── Test 5: Critical account change + no verification → approval prohibited


def test_critical_evidence_approval_strictly_prohibited():
    """Security boundary test: when bank account changed and unverified,
    approval is strictly impossible under all conditions.
    """
    req = _make_hero_request()
    result = run_investigation(
        req,
        verification_available=False,
        enable_secondary_verification=True,
        trusted_contact_reachable=False,
        persist=False,
    )
    assert result.final_action != FinalAction.APPROVE
    assert result.final_action == FinalAction.HUMAN_REVIEW


# ── Test 6: Failure does not erase accumulated evidence ─────────────


def test_failure_preserves_accumulated_evidence():
    """When a failure occurs, prior evidence must remain intact in the ledger."""
    req = _make_hero_request()
    result = run_investigation(req, verification_available=False, persist=False)

    evidence_tools = {e.tool_name for e in result.evidence}
    assert "parse_invoice" in evidence_tools
    assert "check_vendor_history" in evidence_tools
    assert "check_domain" in evidence_tools
    assert "compare_payment_account" in evidence_tools
    assert "request_independent_verification" in evidence_tools


# ── Test 7: Failure appears in persisted SQLite trace ────────────────


def test_failure_persisted_in_sqlite_trace():
    """Trace entries with phase='FAILURE' must be saved to and queryable from SQLite."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db = tf.name

    try:
        req = _make_hero_request(request_id="VF-PERSIST-FAIL")
        run_investigation(
            req,
            verification_available=False,
            db_path=temp_db,
            persist=True,
        )

        trace = get_case_trace("VF-PERSIST-FAIL", db_path=temp_db)
        phases = [e["phase"] for e in trace]
        assert "FAILURE" in phases
        assert "ADAPT" in phases
        assert "FINAL" in phases
    finally:
        Path(temp_db).unlink(missing_ok=True)


# ── Test 8: Deterministic replay invariance ──────────────────────────


def test_replay_produces_identical_trace():
    """Replaying the investigation produces an identical sequence of steps."""
    req = _make_hero_request(request_id="VF-REPLAY")
    res1 = run_investigation(req, verification_available=False, persist=False)
    res2 = run_investigation(req, verification_available=False, persist=False)

    assert [e.phase for e in res1.trace] == [e.phase for e in res2.trace]
    assert [e.tool for e in res1.trace] == [e.tool for e in res2.trace]
    assert res1.final_action == res2.final_action
    assert res1.risk_score == res2.risk_score


# ── Test 9: Failure injection switches ───────────────────────────────


def test_failure_injection_switches():
    """Controllable failure injection flags override environment conditions."""
    req = _make_hero_request()
    injection = FailureInjectionConfig(
        verification_service_offline=True,
        trusted_contact_unreachable=True,
    )
    # Even if verification_available was passed as True, injection forces it False
    result = run_investigation(
        req,
        verification_available=True,
        enable_secondary_verification=True,
        trusted_contact_reachable=True,
        failure_injection=injection,
        persist=False,
    )
    assert result.final_action == FinalAction.HUMAN_REVIEW
    assert len(result.failures) == 2


# ── Test 10: Trusted contact tool unit tests ─────────────────────────


def test_trusted_contact_tool_outcomes():
    # 1. No contact in database
    res_none = verify_via_trusted_contact("Acme", None)
    assert res_none.status == ToolStatus.UNAVAILABLE

    # 2. Contact unreachable
    res_unreach = verify_via_trusted_contact("Acme", "+91-9000000001", contact_reachable=False)
    assert res_unreach.status == ToolStatus.UNAVAILABLE

    # 3. Contact confirms
    res_ok = verify_via_trusted_contact(
        "Acme", "+91-9000000001", contact_reachable=True, contact_confirmed=True
    )
    assert res_ok.status == ToolStatus.SUCCESS

    # 4. Contact repudiates (conflict)
    res_fraud = verify_via_trusted_contact(
        "Acme", "+91-9000000001", contact_reachable=True, contact_confirmed=False
    )
    assert res_fraud.status == ToolStatus.CONFLICT
