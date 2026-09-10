"""Input trust boundary and telemetry utilities.

Security architecture:
The primary security defense is the strict architectural trust boundary:
    UNTRUSTED DOCUMENT
            ↓
    LLM extraction only
            ↓
    Pydantic schema validation
            ↓
    Deterministic tools & evidence ledger
            ↓
    Deterministic policy engine
            ↓
    Explicit runtime authorization gate

Keyword scanning in this module serves strictly as auxiliary TELEMETRY
for logging and risk signaling, NEVER as the primary security boundary.
"""

from __future__ import annotations

import re
from typing import Any

from ..models.schemas import PaymentRequest

# Telemetry keywords — used only for logging and anomaly telemetry flags
_SUSPICIOUS_PATTERNS = [
    r"ignore (?:all )?previous instructions",
    r"system override",
    r"you are now",
    r"debug mode",
    r"disregard prior",
    r"jailbreak",
    r"drop table",
    r"exec\s*\(",
    r"<script",
]


def wrap_untrusted_input(raw_text: str) -> str:
    """Enclose untrusted external text in explicit document boundary tags.

    This ensures the downstream LLM sees the text purely as passive data
    rather than instructions.
    """
    cleaned = raw_text.replace("\x00", "")  # Strip null bytes
    return f"<untrusted_document>\n{cleaned}\n</untrusted_document>"


def scan_telemetry_signals(raw_text: str) -> list[str]:
    """Scan untrusted input for telemetry signals.

    NOTE: This is telemetry only, NOT an authorization boundary.
    """
    signals = []
    lower = raw_text.lower()
    for pat in _SUSPICIOUS_PATTERNS:
        if re.search(pat, lower):
            signals.append(f"telemetry_pattern_match:{pat}")
    return signals


def validate_request_sanity(request: PaymentRequest) -> tuple[bool, str]:
    """Validate numerical and semantic sanity of a payment request."""
    if request.amount is None:
        return False, "Invoice amount is missing"
    if request.amount <= 0:
        return False, f"Invoice amount must be positive, got {request.amount}"
    if not request.vendor_name or len(request.vendor_name.strip()) == 0:
        return False, "Vendor name is empty"
    if not request.requested_account or len(request.requested_account.strip()) == 0:
        return False, "Requested account is empty"
    return True, "Valid"
