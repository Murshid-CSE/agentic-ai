"""Tests for FastAPI endpoints."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_investigate_and_query_endpoints():
    payload = {
        "request_id": "API-TEST-001",
        "vendor_name": "Acme Supplies",
        "sender_email": "accounts@acme.in",
        "sender_domain": "acme.in",
        "invoice_number": "INV-API-1",
        "amount": 42000,
        "requested_account": "BANK-ACME-001",
        "urgency": "normal",
    }

    # 1. Run investigation
    res = client.post("/investigate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["request_id"] == "API-TEST-001"
    assert data["final_action"] == "APPROVE"
    assert data["risk_score"] == 0
    assert "risk_signals" in data

    # 2. List cases
    res_cases = client.get("/cases")
    assert res_cases.status_code == 200
    cases = res_cases.json()
    assert any(c["request_id"] == "API-TEST-001" for c in cases)

    # 3. Get case detail
    res_case = client.get("/cases/API-TEST-001")
    assert res_case.status_code == 200
    detail = res_case.json()
    assert detail["request_id"] == "API-TEST-001"
    assert detail["final_action"] == "APPROVE"

    # 4. Get case trace
    res_trace = client.get("/cases/API-TEST-001/trace")
    assert res_trace.status_code == 200
    trace = res_trace.json()
    assert len(trace) > 0
    assert trace[0]["phase"] == "OBSERVE"

    # 5. Get case evidence
    res_ev = client.get("/cases/API-TEST-001/evidence")
    assert res_ev.status_code == 200
    evidence = res_ev.json()
    assert len(evidence["tool_calls"]) == 4


def test_case_not_found():
    res = client.get("/cases/NONEXISTENT_CASE_ID_999")
    assert res.status_code == 404


def test_extract_endpoint():
    payload = {
        "text": "Please pay Acme Supplies invoice INV-1001 for 42000 USD to BANK-ACME-001 immediately.",
        "sender_email": "accounts@acme.in",
    }
    res = client.post("/extract", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["claim"]["vendor_name"] == "Acme Supplies"
    assert data["claim"]["amount"] == 42000.0


def test_investigate_raw_endpoint():
    payload = {
        "text": "From Acme Supplies: Please update bank details to BANK-ACME-999 for invoice 4938 ($125,000). Urgent.",
        "sender_email": "billing@acme-payments.co",
        "default_vendor": "Acme Supplies",
    }
    res = client.post("/investigate/raw", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["final_action"] == "HUMAN_REVIEW"
    assert data["risk_score"] == 100
    assert data["adaptations"] == 1

