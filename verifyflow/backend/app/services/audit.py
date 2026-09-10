"""Audit and evidence ledger service for VerifyFlow."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..database.db import (
    get_case,
    get_case_evidence,
    get_case_trace,
    init_db,
    list_cases,
    save_investigation,
)
from ..models.schemas import InvestigationResult, PaymentRequest


class AuditLogger:
    """Audit logger providing in-memory logging and SQLite evidence ledger integration."""

    def __init__(self, db_path: Path | str | None = None) -> None:
        self.db_path = db_path
        self.entries: list[dict[str, str]] = []
        if db_path is not None:
            init_db(db_path)

    def log(self, event: str, detail: str = "") -> None:
        """Record a timestamped audit event in memory."""
        self.entries.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "detail": detail,
        })

    def get_log(self) -> list[dict[str, str]]:
        """Return the in-memory audit log entries."""
        return list(self.entries)

    def clear(self) -> None:
        """Reset the in-memory audit log entries."""
        self.entries.clear()

    def record_investigation(
        self,
        request: PaymentRequest,
        result: InvestigationResult,
    ) -> int:
        """Persist a complete investigation ledger to SQLite."""
        return save_investigation(request, result, db_path=self.db_path)

    def get_case(self, case_id: str | int) -> dict[str, Any] | None:
        """Retrieve a persisted case from SQLite."""
        return get_case(case_id, db_path=self.db_path)

    def get_case_trace(self, case_id: str | int) -> list[dict[str, Any]]:
        """Retrieve a case's chronological trace from SQLite."""
        return get_case_trace(case_id, db_path=self.db_path)

    def get_case_evidence(self, case_id: str | int) -> dict[str, Any]:
        """Retrieve a case's evidence items from SQLite."""
        return get_case_evidence(case_id, db_path=self.db_path)

    def list_cases(self, limit: int = 50) -> list[dict[str, Any]]:
        """List cases from SQLite."""
        return list_cases(limit=limit, db_path=self.db_path)
