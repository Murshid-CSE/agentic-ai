"""Tool: Check sender domain against the trusted vendor domain."""

from ..models.schemas import PaymentRequest, ToolResult, ToolStatus


def check_domain(
    request: PaymentRequest,
    known_domain: str | None,
) -> ToolResult:
    """Compare the sender domain from the payment request against the known vendor domain."""

    if not known_domain:
        return ToolResult(
            tool_name="check_domain",
            status=ToolStatus.FAILED,
            summary="Known vendor domain is unavailable.",
            confidence=0.0,
        )

    actual = request.sender_domain.lower().strip()
    expected = known_domain.lower().strip()

    if actual == expected:
        return ToolResult(
            tool_name="check_domain",
            status=ToolStatus.SUCCESS,
            summary="Sender domain matches the trusted vendor domain.",
            evidence={
                "sender_domain": actual,
                "known_domain": expected,
                "match": True,
            },
            confidence=0.99,
        )

    return ToolResult(
        tool_name="check_domain",
        status=ToolStatus.CONFLICT,
        summary="Sender domain does not match the trusted vendor domain.",
        evidence={
            "sender_domain": actual,
            "known_domain": expected,
            "match": False,
        },
        confidence=0.98,
    )
