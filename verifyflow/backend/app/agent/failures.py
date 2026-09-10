"""Failure modeling and failure injection configuration for VerifyFlow.

Provides explicit failure categories and controlled failure injection
switches to evaluate and demonstrate runtime agent adaptation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FailureCategory(str, Enum):
    """Explicit taxonomy of runtime operational and evidence failures."""

    TOOL_UNAVAILABLE = "TOOL_UNAVAILABLE"
    INVALID_RESULT = "INVALID_RESULT"
    TIMEOUT = "TIMEOUT"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class FailureRecord(BaseModel):
    """A concrete failure event recognized and recorded by the agent."""

    tool_name: str
    category: FailureCategory
    detail: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class FailureInjectionConfig(BaseModel):
    """Controllable environment switches for testing and demo injection."""

    verification_service_offline: bool = False
    trusted_contact_unreachable: bool = False
    domain_lookup_failure: bool = False
    simulate_timeout: bool = False
