"""Tool: Request independent verification through a previously trusted contact."""

from ..models.schemas import ToolResult, ToolStatus


def request_independent_verification(
    *,
    available: bool,
    verified: bool | None = None,
) -> ToolResult:
    """Simulate verification through a previously trusted contact channel.

    In the MVP this is deterministic — the caller controls whether
    verification is available and what the outcome is.
    """

    if not available:
        return ToolResult(
            tool_name="request_independent_verification",
            status=ToolStatus.UNAVAILABLE,
            summary="Trusted independent verification channel is unavailable.",
            evidence={
                "verification_available": False,
            },
            confidence=1.0,
        )

    if verified is True:
        return ToolResult(
            tool_name="request_independent_verification",
            status=ToolStatus.SUCCESS,
            summary="Vendor independently verified the payment change.",
            evidence={
                "verification_available": True,
                "verified": True,
            },
            confidence=0.99,
        )

    if verified is False:
        return ToolResult(
            tool_name="request_independent_verification",
            status=ToolStatus.CONFLICT,
            summary="Independent verification failed.",
            evidence={
                "verification_available": True,
                "verified": False,
            },
            confidence=0.99,
        )

    return ToolResult(
        tool_name="request_independent_verification",
        status=ToolStatus.UNAVAILABLE,
        summary="Verification result is inconclusive.",
        evidence={
            "verification_available": True,
            "verified": None,
        },
        confidence=0.5,
    )
