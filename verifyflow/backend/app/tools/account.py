"""Tool: Compare the requested payment account against the trusted account."""

from ..models.schemas import PaymentRequest, ToolResult, ToolStatus


def compare_payment_account(
    request: PaymentRequest,
    known_account: str | None,
) -> ToolResult:
    """Detect bank-account changes between the request and trusted records."""

    if not known_account:
        return ToolResult(
            tool_name="compare_payment_account",
            status=ToolStatus.FAILED,
            summary="No trusted payment account is available.",
            confidence=0.0,
        )

    requested = request.requested_account.strip()
    known = known_account.strip()

    if requested == known:
        return ToolResult(
            tool_name="compare_payment_account",
            status=ToolStatus.SUCCESS,
            summary="Requested payment account matches the trusted account.",
            evidence={
                "known_account": known,
                "requested_account": requested,
                "changed": False,
            },
            confidence=0.99,
        )

    return ToolResult(
        tool_name="compare_payment_account",
        status=ToolStatus.CONFLICT,
        summary="Requested payment account differs from the trusted account.",
        evidence={
            "known_account": known,
            "requested_account": requested,
            "changed": True,
        },
        confidence=0.99,
    )
