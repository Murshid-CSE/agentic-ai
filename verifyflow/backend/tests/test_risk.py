"""Tests for deterministic risk signal extraction and scoring."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.risk import compute_risk_level, extract_risk_signals
from app.models.schemas import (
    PaymentRequest,
    RiskLevel,
    RiskSignalType,
    ToolResult,
    ToolStatus,
)


def _make_req(**overrides) -> PaymentRequest:
    defaults = {
        "request_id": "TEST-RISK",
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


def test_clean_request_zero_risk():
    req = _make_req()
    evidence_map = {
        "check_vendor_history": ToolResult(
            tool_name="check_vendor_history",
            status=ToolStatus.SUCCESS,
            summary="Vendor found",
            evidence={
                "vendor_found": True,
                "historical_amount_max": 75000,
            },
        ),
        "check_domain": ToolResult(
            tool_name="check_domain",
            status=ToolStatus.SUCCESS,
            summary="Domain matches",
            evidence={"match": True, "known_domain": "acme.in"},
        ),
        "compare_payment_account": ToolResult(
            tool_name="compare_payment_account",
            status=ToolStatus.SUCCESS,
            summary="Account matches",
            evidence={"changed": False, "known_account": "BANK-ACME-001"},
        ),
    }

    assessment = extract_risk_signals(req, evidence_map)
    assert assessment.score == 0
    assert assessment.level == RiskLevel.LOW
    assert len(assessment.signals) == 0


def test_domain_mismatch_signal():
    req = _make_req(sender_domain="acme-fake.co")
    evidence_map = {
        "check_domain": ToolResult(
            tool_name="check_domain",
            status=ToolStatus.CONFLICT,
            summary="Domain mismatch",
            evidence={"match": False, "known_domain": "acme.in"},
        )
    }

    assessment = extract_risk_signals(req, evidence_map)
    assert assessment.score == 30
    assert assessment.level == RiskLevel.MEDIUM
    sig_types = [s.signal_type for s in assessment.signals]
    assert RiskSignalType.DOMAIN_MISMATCH in sig_types


def test_account_changed_signal():
    req = _make_req(requested_account="BANK-FRAUD-999")
    evidence_map = {
        "compare_payment_account": ToolResult(
            tool_name="compare_payment_account",
            status=ToolStatus.CONFLICT,
            summary="Account changed",
            evidence={"changed": True, "known_account": "BANK-ACME-001"},
        )
    }

    assessment = extract_risk_signals(req, evidence_map)
    assert assessment.score == 40
    assert assessment.level == RiskLevel.MEDIUM
    sig_types = [s.signal_type for s in assessment.signals]
    assert RiskSignalType.ACCOUNT_CHANGED in sig_types


def test_unusual_amount_and_urgent_request():
    req = _make_req(amount=120000, urgency="urgent")
    evidence_map = {
        "check_vendor_history": ToolResult(
            tool_name="check_vendor_history",
            status=ToolStatus.SUCCESS,
            summary="Vendor found",
            evidence={
                "vendor_found": True,
                "historical_amount_max": 75000,
            },
        )
    }

    assessment = extract_risk_signals(req, evidence_map)
    # Unusual amount (15) + Urgent (10) = 25 -> MEDIUM (16-45)
    assert assessment.score == 25
    assert assessment.level == RiskLevel.MEDIUM
    sig_types = {s.signal_type for s in assessment.signals}
    assert RiskSignalType.UNUSUAL_AMOUNT in sig_types
    assert RiskSignalType.URGENT_REQUEST in sig_types


def test_hero_scenario_critical_risk():
    """Hero scenario has:
    - Domain mismatch (+30)
    - Account changed (+40)
    - Unusual amount (+15)
    - Urgent (+10)
    - Verification unavailable (+20)
    Total = 115 -> capped at 100 -> CRITICAL
    """
    req = _make_req(
        sender_domain="acme-payments.co",
        requested_account="BANK-ACME-999",
        amount=125000,
        urgency="urgent",
    )
    evidence_map = {
        "check_vendor_history": ToolResult(
            tool_name="check_vendor_history",
            status=ToolStatus.SUCCESS,
            summary="Vendor found",
            evidence={
                "vendor_found": True,
                "historical_amount_max": 75000,
            },
        ),
        "check_domain": ToolResult(
            tool_name="check_domain",
            status=ToolStatus.CONFLICT,
            summary="Domain mismatch",
            evidence={"match": False, "known_domain": "acme.in"},
        ),
        "compare_payment_account": ToolResult(
            tool_name="compare_payment_account",
            status=ToolStatus.CONFLICT,
            summary="Account changed",
            evidence={"changed": True, "known_account": "BANK-ACME-001"},
        ),
        "request_independent_verification": ToolResult(
            tool_name="request_independent_verification",
            status=ToolStatus.UNAVAILABLE,
            summary="Verification unavailable",
            evidence={"verification_available": False},
        ),
    }

    assessment = extract_risk_signals(req, evidence_map)
    assert assessment.score == 100
    assert assessment.level == RiskLevel.CRITICAL
    assert len(assessment.signals) == 5


def test_compute_risk_level_boundaries():
    assert compute_risk_level(0) == RiskLevel.LOW
    assert compute_risk_level(15) == RiskLevel.LOW
    assert compute_risk_level(16) == RiskLevel.MEDIUM
    assert compute_risk_level(45) == RiskLevel.MEDIUM
    assert compute_risk_level(46) == RiskLevel.HIGH
    assert compute_risk_level(75) == RiskLevel.HIGH
    assert compute_risk_level(76) == RiskLevel.CRITICAL
    assert compute_risk_level(100) == RiskLevel.CRITICAL
