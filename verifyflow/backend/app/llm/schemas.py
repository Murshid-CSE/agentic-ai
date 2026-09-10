"""Pydantic schemas for LLM entity extraction and natural-language requests."""

from typing import Any

from pydantic import BaseModel, Field


class ExtractedPaymentClaim(BaseModel):
    """Structured entities and claims extracted from unstructured natural language."""

    vendor_name: str | None = Field(
        default=None,
        description="The commercial organization or contractor requesting payment.",
    )
    invoice_number: str | None = Field(
        default=None,
        description="Identifier of the specific invoice mentioned in the request.",
    )
    amount: float | None = Field(
        default=None,
        description="Monetary amount requested for payment.",
    )
    requested_account: str | None = Field(
        default=None,
        description="Bank account number, IBAN, or routing target specified for payment.",
    )
    sender_email: str | None = Field(
        default=None,
        description="Email address of the sender, if explicitly mentioned or provided.",
    )
    sender_domain: str | None = Field(
        default=None,
        description="Internet domain part of the sender's email address.",
    )
    requested_account_change: bool = Field(
        default=False,
        description="Whether the sender claims a change, update, or migration of payment details.",
    )
    urgency: str = Field(
        default="normal",
        description="Operational urgency level ('normal' or 'urgent').",
    )
    claims: list[str] = Field(
        default_factory=list,
        description="Key factual claims made by the sender (e.g., 'banking relationship migrated').",
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Extraction confidence score.",
    )


class ExtractionResult(BaseModel):
    """Container for the extraction outcome, metadata, and error handling."""

    success: bool
    claim: ExtractedPaymentClaim | None = None
    provider_used: str = "unknown"
    error: str | None = None
    raw_response: str | None = None


class RawInvestigationRequest(BaseModel):
    """Payload for submitting unformatted email or message text to VerifyFlow."""

    text: str = Field(..., description="Raw text of email, invoice note, or message.")
    request_id: str | None = Field(
        default=None,
        description="Optional tracking identifier. If omitted, one will be generated.",
    )
    sender_email: str | None = Field(
        default=None,
        description="Sender email from headers (e.g. 'billing@acme-payments.co').",
    )
    default_vendor: str | None = Field(
        default=None,
        description="Fallback vendor name if not mentioned in the email body.",
    )
    verification_available: bool = Field(
        default=False,
        description="Whether independent out-of-band verification channel is reachable.",
    )
