"""Tool: Check vendor history against the trusted vendor registry."""

import json
from pathlib import Path

from ..models.schemas import PaymentRequest, ToolResult, ToolStatus


VENDOR_FILE = Path(__file__).resolve().parents[3] / "data" / "vendors.json"


def load_vendors() -> list[dict]:
    """Load the vendor registry from disk."""
    with VENDOR_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def check_vendor_history(request: PaymentRequest) -> ToolResult:
    """Compare the payment request vendor against known vendor records."""
    vendors = load_vendors()

    vendor = next(
        (
            item
            for item in vendors
            if item["name"].lower() == request.vendor_name.lower()
        ),
        None,
    )

    if vendor is None:
        return ToolResult(
            tool_name="check_vendor_history",
            status=ToolStatus.CONFLICT,
            summary="Vendor was not found in the trusted vendor registry.",
            evidence={
                "vendor_found": False,
                "vendor": request.vendor_name,
            },
            confidence=0.98,
        )

    return ToolResult(
        tool_name="check_vendor_history",
        status=ToolStatus.SUCCESS,
        summary="Vendor exists in the trusted registry.",
        evidence={
            "vendor_found": True,
            "known_domain": vendor["known_domain"],
            "known_account": vendor["known_account"],
            "trusted_contact": vendor["trusted_contact"],
            "historical_amount_avg": vendor["historical_amount_avg"],
            "historical_amount_max": vendor["historical_amount_max"],
        },
        confidence=0.99,
    )
