"""Tool: Parse invoice metadata from a payment request."""

from ..models.schemas import PaymentRequest, ToolResult, ToolStatus


def parse_invoice(request: PaymentRequest) -> ToolResult:
    """Extract vendor, amount, account details, and invoice metadata.

    For Milestone 1, this is deterministic — it validates that the
    payment request contains the required metadata fields.
    Actual PDF parsing will be added in Milestone 4 (LLM Integration).
    """

    if not request.invoice_number:
        return ToolResult(
            tool_name="parse_invoice",
            status=ToolStatus.FAILED,
            summary="Invoice number is missing.",
            confidence=0.0,
        )

    return ToolResult(
        tool_name="parse_invoice",
        status=ToolStatus.SUCCESS,
        summary="Payment request contains the required invoice metadata.",
        evidence={
            "invoice_number": request.invoice_number,
            "amount": request.amount,
            "vendor": request.vendor_name,
            "urgency": request.urgency,
        },
        confidence=0.99,
    )
