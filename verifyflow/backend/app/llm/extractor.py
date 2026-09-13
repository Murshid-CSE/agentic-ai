"""Entity extraction and normalization engine using structured LLM outputs."""

from __future__ import annotations

import json
import re
from typing import Any
from uuid import uuid4

from pydantic import ValidationError

from ..models.schemas import PaymentRequest
from .client import DeterministicFallbackProvider, LLMProvider, get_llm_provider
from .prompts import SYSTEM_EXTRACTION_PROMPT, USER_EXTRACTION_TEMPLATE
from .schemas import ExtractedPaymentClaim, ExtractionResult, RawInvestigationRequest


def clean_json_response(raw_text: str) -> str:
    """Strip markdown formatting, code fences, or leading prose from LLM text."""
    text = raw_text.strip()
    if text.startswith("```"):
        # Match inside ```json ... ```
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()

    # Find the outermost JSON object
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        text = text[first_brace : last_brace + 1]

    return text


def extract_payment_claim(
    text: str,
    sender_header: str | None = None,
    provider: LLMProvider | None = None,
) -> ExtractionResult:
    """Extract structured payment facts and claims from unstructured text.

    Parameters
    ----------
    text:
        The raw body of the message, email, or invoice note.
    sender_header:
        Optional email address from the email header (e.g. 'accounts@acme.in').
    provider:
        Optional explicit LLM provider instance; otherwise auto-detected.

    Returns
    -------
    ExtractionResult
        Result containing the validated ExtractedPaymentClaim or error context.
    """
    llm = provider or get_llm_provider()
    user_prompt = USER_EXTRACTION_TEMPLATE.format(
        sender_header=sender_header or "Not provided",
        text=text,
    )

    raw_response = ""
    try:
        raw_response = llm.generate_json(SYSTEM_EXTRACTION_PROMPT, user_prompt)
        cleaned = clean_json_response(raw_response)
        data = json.loads(cleaned)

        # Merge sender_header if missing from extracted data
        if sender_header and not data.get("sender_email"):
            data["sender_email"] = sender_header
        if data.get("sender_email") and not data.get("sender_domain"):
            if "@" in data["sender_email"]:
                data["sender_domain"] = data["sender_email"].split("@")[-1]

        claim = ExtractedPaymentClaim.model_validate(data)
        return ExtractionResult(
            success=True,
            claim=claim,
            provider_used=llm.name,
            raw_response=raw_response,
        )

    except Exception as err:
        # Graceful fallback: If LLM output was malformed or provider errored, use deterministic fallback
        if not isinstance(llm, DeterministicFallbackProvider):
            fallback = DeterministicFallbackProvider()
            try:
                fb_raw = fallback.generate_json(SYSTEM_EXTRACTION_PROMPT, user_prompt)
                fb_data = json.loads(clean_json_response(fb_raw))
                if sender_header and not fb_data.get("sender_email"):
                    fb_data["sender_email"] = sender_header
                if fb_data.get("sender_email") and not fb_data.get("sender_domain"):
                    fb_data["sender_domain"] = fb_data["sender_email"].split("@")[-1]

                claim = ExtractedPaymentClaim.model_validate(fb_data)
                return ExtractionResult(
                    success=True,
                    claim=claim,
                    provider_used=f"{llm.name}_with_fallback",
                    error=f"Primary model failed ({str(err)}); recovered with deterministic fallback",
                    raw_response=raw_response,
                )
            except Exception:
                pass

        return ExtractionResult(
            success=False,
            claim=None,
            provider_used=llm.name,
            error=f"LLM extraction failed: {str(err)}",
            raw_response=raw_response,
        )


def raw_text_to_payment_request(
    raw_req: RawInvestigationRequest,
    provider: LLMProvider | None = None,
) -> tuple[PaymentRequest, ExtractionResult]:
    """Convert an unformatted raw text request into a validated PaymentRequest."""
    extraction = extract_payment_claim(
        raw_req.text,
        sender_header=raw_req.sender_email,
        provider=provider,
    )

    req_id = raw_req.request_id or f"VF-RAW-{uuid4().hex[:6].upper()}"

    if not extraction.success or not extraction.claim:
        # Fail-closed default request that triggers deterministic verification failure
        sender_email = raw_req.sender_email or "unknown@unverified.org"
        domain = sender_email.split("@")[-1] if "@" in sender_email else "unverified.org"
        return (
            PaymentRequest(
                request_id=req_id,
                vendor_name=raw_req.default_vendor or "Unextracted Vendor",
                sender_email=sender_email,
                sender_domain=domain,
                invoice_number="INV-UNEXTRACTED",
                amount=1.0,
                requested_account="UNKNOWN-ACCOUNT",
                urgency="urgent",
            ),
            extraction,
        )

    claim = extraction.claim

    # Resolve email and domain
    sender_email = claim.sender_email or raw_req.sender_email or "unknown@unverified.org"
    sender_domain = (
        claim.sender_domain
        or (sender_email.split("@")[-1] if "@" in sender_email else "unverified.org")
    )

    vendor_name = claim.vendor_name or raw_req.default_vendor or "Unknown Vendor"
    invoice_num = claim.invoice_number or "INV-UNKNOWN"
    amount = float(claim.amount) if claim.amount is not None else 1.0
    account = claim.requested_account or "UNKNOWN-ACCOUNT"
    urgency = claim.urgency or "normal"

    payment_request = PaymentRequest(
        request_id=req_id,
        vendor_name=vendor_name,
        sender_email=sender_email,
        sender_domain=sender_domain,
        invoice_number=invoice_num,
        amount=amount,
        requested_account=account,
        urgency=urgency,
    )

    return payment_request, extraction
