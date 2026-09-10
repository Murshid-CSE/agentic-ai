"""Secondary verification tool — out-of-band vendor trusted contact verification.

Called when primary automated verification channels fail or return UNAVAILABLE.
Attempts contact with the secondary phone/security point of contact in trusted vendor records.
"""

from __future__ import annotations

from typing import Any

from ..models.schemas import ToolResult, ToolStatus


def verify_via_trusted_contact(
    vendor_name: str,
    trusted_contact: str | None,
    *,
    contact_reachable: bool = False,
    contact_confirmed: bool | None = None,
) -> ToolResult:
    """Attempt secondary out-of-band verification with vendor's registered contact.

    Parameters
    ----------
    vendor_name:
        Name of the vendor.
    trusted_contact:
        Registered phone number or security contact from vendor database.
    contact_reachable:
        Whether the trusted contact phone/call was reachable.
    contact_confirmed:
        If reachable, whether the contact verified the account change.

    Returns
    -------
    ToolResult
        Execution status and structured evidence.
    """
    tool_name = "verify_via_trusted_contact"

    if not trusted_contact:
        return ToolResult(
            tool_name=tool_name,
            status=ToolStatus.UNAVAILABLE,
            summary=f"No registered trusted phone contact found for vendor '{vendor_name}'.",
            evidence={
                "vendor_name": vendor_name,
                "trusted_contact": None,
                "reachable": False,
                "confirmed": None,
            },
            confidence=0.90,
        )

    if not contact_reachable:
        return ToolResult(
            tool_name=tool_name,
            status=ToolStatus.UNAVAILABLE,
            summary=f"Trusted contact ({trusted_contact}) for '{vendor_name}' was unreachable or did not respond.",
            evidence={
                "vendor_name": vendor_name,
                "trusted_contact": trusted_contact,
                "reachable": False,
                "confirmed": None,
            },
            confidence=0.85,
        )

    if contact_confirmed is True:
        return ToolResult(
            tool_name=tool_name,
            status=ToolStatus.SUCCESS,
            summary=f"Trusted contact ({trusted_contact}) confirmed legitimate payment account migration.",
            evidence={
                "vendor_name": vendor_name,
                "trusted_contact": trusted_contact,
                "reachable": True,
                "confirmed": True,
            },
            confidence=0.95,
        )

    if contact_confirmed is False:
        return ToolResult(
            tool_name=tool_name,
            status=ToolStatus.CONFLICT,
            summary=f"Trusted contact ({trusted_contact}) actively repudiated the payment account change as fraudulent.",
            evidence={
                "vendor_name": vendor_name,
                "trusted_contact": trusted_contact,
                "reachable": True,
                "confirmed": False,
            },
            confidence=0.99,
        )

    # Inconclusive contact response
    return ToolResult(
        tool_name=tool_name,
        status=ToolStatus.CONFLICT,
        summary=f"Trusted contact ({trusted_contact}) was reached but could not authenticate or confirm.",
        evidence={
            "vendor_name": vendor_name,
            "trusted_contact": trusted_contact,
            "reachable": True,
            "confirmed": None,
        },
        confidence=0.70,
    )
