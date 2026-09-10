"""Tests for SQLite evidence ledger persistence and case querying."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.controller import run_investigation
from app.database.db import (
    get_case,
    get_case_evidence,
    get_case_trace,
    init_db,
    list_cases,
    save_investigation,
)
from app.models.schemas import FinalAction, PaymentRequest


def _make_req(**overrides) -> PaymentRequest:
    defaults = {
        "request_id": "DB-TEST-001",
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


def test_db_init_and_save():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db = tf.name

    try:
        init_db(temp_db)
        req = _make_req()
        result = run_investigation(req, persist=False)

        inv_id = save_investigation(req, result, db_path=temp_db)
        assert inv_id > 0

        # Retrieve case by request_id
        case = get_case(req.request_id, db_path=temp_db)
        assert case is not None
        assert case["request_id"] == "DB-TEST-001"
        assert case["final_action"] == FinalAction.APPROVE.value
        assert case["risk_score"] == 0

        # Retrieve case by integer investigation_id
        case_by_id = get_case(inv_id, db_path=temp_db)
        assert case_by_id is not None
        assert case_by_id["id"] == inv_id

        # Retrieve trace
        trace = get_case_trace(req.request_id, db_path=temp_db)
        assert len(trace) > 0
        assert trace[0]["phase"] == "OBSERVE"
        assert trace[-1]["phase"] == "FINAL"

        # Retrieve evidence
        ev = get_case_evidence(req.request_id, db_path=temp_db)
        assert len(ev["tool_calls"]) == 4
        assert len(ev["evidence_items"]) > 0

        # List cases
        cases = list_cases(limit=10, db_path=temp_db)
        assert len(cases) == 1
        assert cases[0]["request_id"] == "DB-TEST-001"
        assert cases[0]["final_action"] == "APPROVE"
    finally:
        Path(temp_db).unlink(missing_ok=True)


def test_persisted_hero_case():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        temp_db = tf.name

    try:
        req = _make_req(
            request_id="DB-HERO-001",
            sender_domain="acme-payments.co",
            requested_account="BANK-ACME-999",
            amount=125000,
            urgency="urgent",
        )
        result = run_investigation(
            req,
            verification_available=False,
            db_path=temp_db,
            persist=True,
        )

        assert result.final_action == FinalAction.HUMAN_REVIEW

        case = get_case("DB-HERO-001", db_path=temp_db)
        assert case is not None
        assert case["final_action"] == "HUMAN_REVIEW"
        assert case["risk_score"] == 100
        assert case["risk_level"] == "CRITICAL"
        assert len(case["risk_signals"]) == 5
        assert len(case["tools_used"]) == 5

        # Check evidence ledger contains discrete items
        ev = get_case_evidence("DB-HERO-001", db_path=temp_db)
        keys = {item["key"] for item in ev["evidence_items"]}
        assert "changed" in keys
        assert "match" in keys
        assert "verification_available" in keys
    finally:
        Path(temp_db).unlink(missing_ok=True)
