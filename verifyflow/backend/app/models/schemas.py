"""Core data models for VerifyFlow."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class FinalAction(str, Enum):
    APPROVE = "APPROVE"
    HOLD = "HOLD"
    QUARANTINE = "QUARANTINE"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class ToolStatus(str, Enum):
    SUCCESS = "SUCCESS"
    CONFLICT = "CONFLICT"
    FAILED = "FAILED"
    UNAVAILABLE = "UNAVAILABLE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskSignalType(str, Enum):
    DOMAIN_MISMATCH = "DOMAIN_MISMATCH"
    ACCOUNT_CHANGED = "ACCOUNT_CHANGED"
    UNKNOWN_VENDOR = "UNKNOWN_VENDOR"
    UNUSUAL_AMOUNT = "UNUSUAL_AMOUNT"
    URGENT_REQUEST = "URGENT_REQUEST"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    VERIFICATION_UNAVAILABLE = "VERIFICATION_UNAVAILABLE"


class ToolResult(BaseModel):
    tool_name: str
    status: ToolStatus
    summary: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class RiskSignal(BaseModel):
    """An individual risk indicator derived deterministically from evidence."""

    signal_type: RiskSignalType
    severity: RiskLevel
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    score_weight: int = Field(ge=0, le=100)
    description: str
    source_tool: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class RiskAssessment(BaseModel):
    """Aggregate risk score and contributing signals."""

    score: int = Field(ge=0, le=100)
    level: RiskLevel
    signals: list[RiskSignal] = Field(default_factory=list)


class PaymentRequest(BaseModel):
    request_id: str
    vendor_name: str
    sender_email: str
    sender_domain: str
    invoice_number: str
    amount: float = Field(gt=0)
    requested_account: str
    urgency: str
    invoice_path: str | None = None


class TraceEntry(BaseModel):
    """A single step in the investigation trace.

    This is the core of the agent's observable reasoning — each entry
    records a state transition with enough context to reconstruct
    the full decision process.
    """

    phase: str  # OBSERVE, DECIDE, ACT, EVALUATE, ADAPT, FINAL
    detail: str
    tool: str | None = None
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class InvestigationResult(BaseModel):
    request_id: str
    final_action: FinalAction
    reason: str
    tools_used: list[str]
    adaptations: int
    evidence: list[ToolResult]
    trace: list[TraceEntry] = Field(default_factory=list)
    risk_score: int = 0
    risk_level: RiskLevel = RiskLevel.LOW
    risk_signals: list[RiskSignal] = Field(default_factory=list)
    failures: list[dict[str, Any]] = Field(default_factory=list)
