"""Tests for the five deterministic verification tools."""

import sys
from pathlib import Path

# Ensure the backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.schemas import PaymentRequest, ToolStatus
from app.tools.invoice import parse_invoice
from app.tools.vendor import check_vendor_history
from app.tools.domain import check_domain
from app.tools.account import compare_payment_account
from app.tools.verification import request_independent_verification


# ── Fixtures ──

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


# ── parse_invoice ──

def test_parse_invoice_success():
    result = parse_invoice(_make_request())
    assert result.status == ToolStatus.SUCCESS
    assert result.evidence["invoice_number"] == "INV-1001"
    assert result.evidence["amount"] == 42000


# ── check_vendor_history ──

def test_vendor_known():
    result = check_vendor_history(_make_request())
    assert result.status == ToolStatus.SUCCESS
    assert result.evidence["vendor_found"] is True
    assert result.evidence["known_domain"] == "acme.in"


def test_vendor_unknown():
    result = check_vendor_history(_make_request(vendor_name="Fake Corp"))
    assert result.status == ToolStatus.CONFLICT
    assert result.evidence["vendor_found"] is False


# ── check_domain ──

def test_domain_match():
    result = check_domain(_make_request(), "acme.in")
    assert result.status == ToolStatus.SUCCESS
    assert result.evidence["match"] is True


def test_domain_conflict():
    result = check_domain(_make_request(sender_domain="acme-payments.co"), "acme.in")
    assert result.status == ToolStatus.CONFLICT
    assert result.evidence["match"] is False


def test_domain_unavailable():
    result = check_domain(_make_request(), None)
    assert result.status == ToolStatus.FAILED


# ── compare_payment_account ──

def test_account_match():
    result = compare_payment_account(_make_request(), "BANK-ACME-001")
    assert result.status == ToolStatus.SUCCESS
    assert result.evidence["changed"] is False


def test_account_changed():
    result = compare_payment_account(
        _make_request(requested_account="BANK-ACME-999"),
        "BANK-ACME-001",
    )
    assert result.status == ToolStatus.CONFLICT
    assert result.evidence["changed"] is True


def test_account_unavailable():
    result = compare_payment_account(_make_request(), None)
    assert result.status == ToolStatus.FAILED


# ── request_independent_verification ──

def test_verification_unavailable():
    result = request_independent_verification(available=False)
    assert result.status == ToolStatus.UNAVAILABLE
    assert result.evidence["verification_available"] is False


def test_verification_success():
    result = request_independent_verification(available=True, verified=True)
    assert result.status == ToolStatus.SUCCESS
    assert result.evidence["verified"] is True


def test_verification_failed():
    result = request_independent_verification(available=True, verified=False)
    assert result.status == ToolStatus.CONFLICT
    assert result.evidence["verified"] is False


def test_verification_inconclusive():
    result = request_independent_verification(available=True, verified=None)
    assert result.status == ToolStatus.UNAVAILABLE
    assert result.evidence["verified"] is None
