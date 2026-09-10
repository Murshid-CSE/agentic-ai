"""SQLite database schema and persistence for VerifyFlow evidence ledger.

Provides structured, ACID-compliant persistence for:
- Payment requests
- Investigation sessions
- Tool calls and granular evidence items
- Deterministic risk signals
- Chronological trace entries (state transitions)
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..models.schemas import (
    InvestigationResult,
    PaymentRequest,
    RiskSignal,
    ToolResult,
    TraceEntry,
)

DEFAULT_DB_FILE = (
    Path(__file__).resolve().parents[3] / "data" / "verifyflow.db"
)


def get_db_path(custom_path: Path | str | None = None) -> str:
    """Resolve database path from argument, environment, or default."""
    if custom_path:
        return str(custom_path)
    env_path = os.environ.get("VERIFYFLOW_DB_PATH")
    if env_path:
        return env_path
    DEFAULT_DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    return str(DEFAULT_DB_FILE)


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Create a configured SQLite database connection."""
    path = get_db_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Path | str | None = None) -> None:
    """Initialize database tables and indexes."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS payment_requests (
                    request_id TEXT PRIMARY KEY,
                    vendor_name TEXT NOT NULL,
                    sender_email TEXT NOT NULL,
                    sender_domain TEXT NOT NULL,
                    invoice_number TEXT NOT NULL,
                    amount REAL NOT NULL,
                    requested_account TEXT NOT NULL,
                    urgency TEXT NOT NULL,
                    invoice_path TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS investigations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL REFERENCES payment_requests(request_id),
                    final_action TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    adaptations INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id INTEGER NOT NULL REFERENCES investigations(id),
                    tool_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    evidence_json TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS evidence_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id INTEGER NOT NULL REFERENCES investigations(id),
                    tool_name TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS risk_signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id INTEGER NOT NULL REFERENCES investigations(id),
                    signal_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    score_weight INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    source_tool TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS trace_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    investigation_id INTEGER NOT NULL REFERENCES investigations(id),
                    phase TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    tool TEXT,
                    timestamp TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_investigations_req
                    ON investigations(request_id);
                CREATE INDEX IF NOT EXISTS idx_tool_calls_inv
                    ON tool_calls(investigation_id);
                CREATE INDEX IF NOT EXISTS idx_evidence_inv
                    ON evidence_items(investigation_id);
                CREATE INDEX IF NOT EXISTS idx_risk_signals_inv
                    ON risk_signals(investigation_id);
                CREATE INDEX IF NOT EXISTS idx_trace_entries_inv
                    ON trace_entries(investigation_id);
                """
            )
    finally:
        conn.close()


def save_investigation(
    request: PaymentRequest,
    result: InvestigationResult,
    db_path: Path | str | None = None,
) -> int:
    """Atomically record a payment request and its complete investigation ledger.

    Returns the generated investigation ID.
    """
    init_db(db_path)
    conn = get_connection(db_path)
    now_iso = datetime.now(timezone.utc).isoformat()

    try:
        with conn:
            # 1. Upsert payment request
            conn.execute(
                """
                INSERT INTO payment_requests (
                    request_id, vendor_name, sender_email, sender_domain,
                    invoice_number, amount, requested_account, urgency,
                    invoice_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    vendor_name=excluded.vendor_name,
                    sender_email=excluded.sender_email,
                    sender_domain=excluded.sender_domain,
                    invoice_number=excluded.invoice_number,
                    amount=excluded.amount,
                    requested_account=excluded.requested_account,
                    urgency=excluded.urgency,
                    invoice_path=excluded.invoice_path;
                """,
                (
                    request.request_id,
                    request.vendor_name,
                    request.sender_email,
                    request.sender_domain,
                    request.invoice_number,
                    request.amount,
                    request.requested_account,
                    request.urgency,
                    request.invoice_path,
                    now_iso,
                ),
            )

            # 2. Insert investigation record
            cursor = conn.execute(
                """
                INSERT INTO investigations (
                    request_id, final_action, reason, risk_score,
                    risk_level, adaptations, created_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    request.request_id,
                    result.final_action.value,
                    result.reason,
                    result.risk_score,
                    result.risk_level.value
                    if hasattr(result.risk_level, "value")
                    else str(result.risk_level),
                    result.adaptations,
                    result.trace[0].timestamp if result.trace else now_iso,
                    result.trace[-1].timestamp if result.trace else now_iso,
                ),
            )
            inv_id = cursor.lastrowid

            # 3. Insert tool calls and individual evidence items
            for tool_res in result.evidence:
                conn.execute(
                    """
                    INSERT INTO tool_calls (
                        investigation_id, tool_name, status, summary,
                        confidence, evidence_json, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        inv_id,
                        tool_res.tool_name,
                        tool_res.status.value,
                        tool_res.summary,
                        tool_res.confidence,
                        json.dumps(tool_res.evidence),
                        now_iso,
                    ),
                )

                for k, v in tool_res.evidence.items():
                    conn.execute(
                        """
                        INSERT INTO evidence_items (
                            investigation_id, tool_name, key, value_json,
                            confidence, timestamp
                        ) VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            inv_id,
                            tool_res.tool_name,
                            k,
                            json.dumps(v),
                            tool_res.confidence,
                            now_iso,
                        ),
                    )

            # 4. Insert risk signals
            for sig in result.risk_signals:
                conn.execute(
                    """
                    INSERT INTO risk_signals (
                        investigation_id, signal_type, severity, confidence,
                        score_weight, description, source_tool, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        inv_id,
                        sig.signal_type.value,
                        sig.severity.value
                        if hasattr(sig.severity, "value")
                        else str(sig.severity),
                        sig.confidence,
                        sig.score_weight,
                        sig.description,
                        sig.source_tool,
                        sig.timestamp,
                    ),
                )

            # 5. Insert trace entries
            for entry in result.trace:
                conn.execute(
                    """
                    INSERT INTO trace_entries (
                        investigation_id, phase, detail, tool, timestamp
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        inv_id,
                        entry.phase,
                        entry.detail,
                        entry.tool,
                        entry.timestamp,
                    ),
                )

            return inv_id
    finally:
        conn.close()


def resolve_investigation_id(
    case_id_or_request_id: str | int,
    conn: sqlite3.Connection,
) -> int | None:
    """Find the latest investigation ID by either integer ID or string request ID."""
    if isinstance(case_id_or_request_id, int) or str(case_id_or_request_id).isdigit():
        row = conn.execute(
            "SELECT id FROM investigations WHERE id = ?",
            (int(case_id_or_request_id),),
        ).fetchone()
        if row:
            return row["id"]

    row = conn.execute(
        "SELECT id FROM investigations WHERE request_id = ? ORDER BY id DESC LIMIT 1",
        (str(case_id_or_request_id),),
    ).fetchone()
    return row["id"] if row else None


def list_cases(
    limit: int = 50,
    db_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """List recent cases with high-level summaries for the dashboard."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            """
            SELECT
                i.id AS investigation_id,
                i.request_id,
                p.vendor_name,
                p.sender_domain,
                p.amount,
                p.urgency,
                i.final_action,
                i.risk_score,
                i.risk_level,
                i.adaptations,
                i.created_at,
                i.completed_at
            FROM investigations i
            JOIN payment_requests p ON i.request_id = p.request_id
            ORDER BY i.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_case(
    case_id_or_request_id: str | int,
    db_path: Path | str | None = None,
) -> dict[str, Any] | None:
    """Retrieve full details of an investigation case."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        inv_id = resolve_investigation_id(case_id_or_request_id, conn)
        if not inv_id:
            return None

        inv_row = conn.execute(
            """
            SELECT i.*, p.vendor_name, p.sender_email, p.sender_domain,
                   p.invoice_number, p.amount, p.requested_account, p.urgency
            FROM investigations i
            JOIN payment_requests p ON i.request_id = p.request_id
            WHERE i.id = ?
            """,
            (inv_id,),
        ).fetchone()

        if not inv_row:
            return None

        case_data = dict(inv_row)

        # Attach risk signals
        signals = conn.execute(
            "SELECT * FROM risk_signals WHERE investigation_id = ? ORDER BY id ASC",
            (inv_id,),
        ).fetchall()
        case_data["risk_signals"] = [dict(s) for s in signals]

        # Attach tool calls summary
        tool_calls = conn.execute(
            "SELECT tool_name, status, summary, confidence, evidence_json, timestamp "
            "FROM tool_calls WHERE investigation_id = ? ORDER BY id ASC",
            (inv_id,),
        ).fetchall()
        case_data["tools_used"] = [
            {
                "tool_name": tc["tool_name"],
                "status": tc["status"],
                "summary": tc["summary"],
                "confidence": tc["confidence"],
                "evidence": json.loads(tc["evidence_json"]),
                "timestamp": tc["timestamp"],
            }
            for tc in tool_calls
        ]

        return case_data
    finally:
        conn.close()


def get_case_trace(
    case_id_or_request_id: str | int,
    db_path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Retrieve the chronological reasoning trace of an investigation."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        inv_id = resolve_investigation_id(case_id_or_request_id, conn)
        if not inv_id:
            return []

        rows = conn.execute(
            "SELECT phase, detail, tool, timestamp FROM trace_entries "
            "WHERE investigation_id = ? ORDER BY id ASC",
            (inv_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_case_evidence(
    case_id_or_request_id: str | int,
    db_path: Path | str | None = None,
) -> dict[str, Any]:
    """Retrieve all structured evidence items and tool results for a case."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        inv_id = resolve_investigation_id(case_id_or_request_id, conn)
        if not inv_id:
            return {"tool_calls": [], "evidence_items": []}

        tc_rows = conn.execute(
            "SELECT tool_name, status, summary, confidence, evidence_json, timestamp "
            "FROM tool_calls WHERE investigation_id = ? ORDER BY id ASC",
            (inv_id,),
        ).fetchall()

        ev_rows = conn.execute(
            "SELECT tool_name, key, value_json, confidence, timestamp "
            "FROM evidence_items WHERE investigation_id = ? ORDER BY id ASC",
            (inv_id,),
        ).fetchall()

        return {
            "investigation_id": inv_id,
            "tool_calls": [
                {
                    "tool_name": r["tool_name"],
                    "status": r["status"],
                    "summary": r["summary"],
                    "confidence": r["confidence"],
                    "evidence": json.loads(r["evidence_json"]),
                    "timestamp": r["timestamp"],
                }
                for r in tc_rows
            ],
            "evidence_items": [
                {
                    "tool_name": r["tool_name"],
                    "key": r["key"],
                    "value": json.loads(r["value_json"]),
                    "confidence": r["confidence"],
                    "timestamp": r["timestamp"],
                }
                for r in ev_rows
            ],
        }
    finally:
        conn.close()
