"""Tests for Milestone 4: LLM extraction, provider abstraction, and fact normalization."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.controller import run_investigation
from app.llm.client import (
    DeterministicFallbackProvider,
    LLMProvider,
    get_llm_provider,
)
from app.llm.extractor import (
    clean_json_response,
    extract_payment_claim,
    raw_text_to_payment_request,
)
from app.llm.schemas import RawInvestigationRequest
from app.models.schemas import FinalAction


class MockCustomLLMProvider(LLMProvider):
    """Mock provider returning fixed JSON response for testing."""

    def __init__(self, json_to_return: str) -> None:
        self.name = "mock_custom"
        self.json_to_return = json_to_return

    def generate_json(self, system_prompt: str, user_prompt: str) -> str:
        return self.json_to_return


def test_clean_json_response():
    # Code fence stripping
    raw_fenced = "```json\n{\"vendor\": \"Acme\"}\n```"
    assert clean_json_response(raw_fenced) == "{\"vendor\": \"Acme\"}"

    # Leading prose stripping
    raw_prose = "Here is the extracted json:\n{\"amount\": 42000}\nHope this helps!"
    assert clean_json_response(raw_prose) == "{\"amount\": 42000}"


def test_provider_resolution():
    prov = get_llm_provider("deterministic")
    assert isinstance(prov, DeterministicFallbackProvider)
    assert prov.name == "deterministic_fallback"


def test_m4_success_criterion_three_differently_worded_requests():
    """M4 Success Criterion:

    Submit three differently worded requests for the same underlying case
    and have VerifyFlow normalize them into equivalent structured facts,
    leading to identical investigation outcomes.
    """
    text_1 = (
        "Hi team, please use our new bank details for invoice 4938. "
        "Kindly transfer 125,000 to account BANK-ACME-999 today. "
        "Urgent month-end closure."
    )
    text_2 = (
        "We've changed our banking partner to BANK-ACME-999. "
        "Kindly update the account and process invoice #4938 for 125000 USD "
        "right away, this is urgent."
    )
    text_3 = (
        "The old account is no longer active. "
        "Pay invoice 4938 ($125,000) to the account BANK-ACME-999 below. "
        "Urgent priority."
    )

    sender = "billing@acme-payments.co"
    default_vendor = "Acme Supplies"

    req_1, ext_1 = raw_text_to_payment_request(
        RawInvestigationRequest(
            text=text_1,
            sender_email=sender,
            default_vendor=default_vendor,
        )
    )
    req_2, ext_2 = raw_text_to_payment_request(
        RawInvestigationRequest(
            text=text_2,
            sender_email=sender,
            default_vendor=default_vendor,
        )
    )
    req_3, ext_3 = raw_text_to_payment_request(
        RawInvestigationRequest(
            text=text_3,
            sender_email=sender,
            default_vendor=default_vendor,
        )
    )

    # 1. Fact Normalization Verification
    for i, req in enumerate([req_1, req_2, req_3], start=1):
        assert req.vendor_name == "Acme Supplies", f"Failed for text_{i}"
        assert req.invoice_number == "INV-4938", f"Failed for text_{i}"
        assert req.amount == 125000.0, f"Failed for text_{i}"
        assert req.requested_account == "BANK-ACME-999", f"Failed for text_{i}"
        assert req.urgency == "urgent", f"Failed for text_{i}"
        assert req.sender_domain == "acme-payments.co", f"Failed for text_{i}"

    # 2. Downstream Investigation Invariance Verification
    res_1 = run_investigation(req_1, persist=False)
    res_2 = run_investigation(req_2, persist=False)
    res_3 = run_investigation(req_3, persist=False)

    for i, res in enumerate([res_1, res_2, res_3], start=1):
        assert res.final_action == FinalAction.HUMAN_REVIEW, f"Action mismatch in text_{i}"
        assert res.risk_score == 100, f"Risk score mismatch in text_{i}"
        assert res.adaptations == 1, f"Adaptations mismatch in text_{i}"
        assert len(res.tools_used) == 5, f"Tools count mismatch in text_{i}"


def test_malformed_llm_output_fails_closed():
    """Invalid model output must fail closed and produce safe handling

    rather than crashing or corrupting authorization.
    """
    mock_bad_llm = MockCustomLLMProvider("INVALID NOT JSON AT ALL {{")
    extraction = extract_payment_claim(
        "Please pay invoice 100",
        provider=mock_bad_llm,
    )
    # The extractor cleanly catches the error and recovers or flags failure
    assert extraction.claim is not None or extraction.success is False

    # Conversion to payment request must produce a valid fail-closed request
    raw_req = RawInvestigationRequest(text="Gibberish invoice")
    req, ext = raw_text_to_payment_request(raw_req, provider=mock_bad_llm)
    assert req.invoice_number is not None
    # Investigation will default-deny
    res = run_investigation(req, persist=False)
    assert res.final_action in (FinalAction.HOLD, FinalAction.HUMAN_REVIEW)
    assert res.final_action != FinalAction.APPROVE


def test_claims_extraction():
    text = (
        "Acme Supplies payment notice: Our bank account has changed to BANK-ACME-999. "
        "Invoice INV-1001 for 42000. Normal priority."
    )
    res = extract_payment_claim(text)
    assert res.success is True
    assert res.claim is not None
    assert res.claim.requested_account_change is True
    assert len(res.claim.claims) > 0
