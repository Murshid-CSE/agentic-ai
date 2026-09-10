"""VerifyFlow — Agentic AI payment-risk verification system.

FastAPI application entry point providing investigation, case audit,
natural-language entity extraction, and frontend command-center APIs.
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .agent.controller import run_investigation
from .database.db import (
    get_case,
    get_case_evidence,
    get_case_trace,
    list_cases,
)
from .evaluation import BenchmarkRunner, execute_benchmark
from .llm.extractor import extract_payment_claim, raw_text_to_payment_request
from .llm.schemas import ExtractionResult, RawInvestigationRequest
from .models.schemas import InvestigationResult, PaymentRequest

app = FastAPI(
    title="VerifyFlow",
    description="Agentic AI security / payment-risk verification workflow",
    version="0.5.0",
)

# Enable CORS for React frontend (Vite default port 5173, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEMO_CASES_DIR = Path(__file__).resolve().parents[2] / "data" / "demo_cases"


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/demo-cases")
def get_demo_cases():
    """Return pre-configured demo cases for quick selection in the frontend."""
    cases = []
    if DEMO_CASES_DIR.exists():
        for file in sorted(DEMO_CASES_DIR.glob("*.json")):
            try:
                with file.open("r", encoding="utf-8") as f:
                    cases.append(json.load(f))
            except Exception:
                pass
    return cases


@app.post("/investigate", response_model=InvestigationResult)
def investigate(
    request: PaymentRequest,
    verification_available: bool = Query(default=False),
    verification_verified: bool | None = Query(default=None),
    enable_secondary_verification: bool = Query(default=False),
    trusted_contact_reachable: bool = Query(default=False),
    trusted_contact_confirmed: bool | None = Query(default=None),
):
    """Run a payment-change investigation from structured request data with failure injection controls."""
    return run_investigation(
        request,
        verification_available=verification_available,
        verification_verified=verification_verified,
        enable_secondary_verification=enable_secondary_verification,
        trusted_contact_reachable=trusted_contact_reachable,
        trusted_contact_confirmed=trusted_contact_confirmed,
    )


@app.post("/extract", response_model=ExtractionResult)
def extract_entities(raw_req: RawInvestigationRequest):
    """Extract structured entities and claims from raw natural language text without running full investigation."""
    return extract_payment_claim(
        raw_req.text,
        sender_header=raw_req.sender_email,
    )


@app.post("/investigate/raw", response_model=InvestigationResult)
def investigate_raw(
    raw_req: RawInvestigationRequest,
    enable_secondary_verification: bool = Query(default=False),
    trusted_contact_reachable: bool = Query(default=False),
    trusted_contact_confirmed: bool | None = Query(default=None),
):
    """Extract structured facts from messy natural language or emails, and run full payment risk investigation."""
    payment_request, extraction = raw_text_to_payment_request(raw_req)

    return run_investigation(
        payment_request,
        verification_available=raw_req.verification_available,
        enable_secondary_verification=enable_secondary_verification,
        trusted_contact_reachable=trusted_contact_reachable,
        trusted_contact_confirmed=trusted_contact_confirmed,
    )


@app.get("/cases")
def get_cases(limit: int = Query(default=50, ge=1, le=200)):
    """List recent investigation cases with high-level summaries."""
    return list_cases(limit=limit)


@app.get("/cases/{case_id}")
def get_case_detail(case_id: str):
    """Retrieve full details of a specific investigation case."""
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    return case


@app.get("/cases/{case_id}/trace")
def get_case_trace_endpoint(case_id: str):
    """Retrieve the chronological reasoning trace for an investigation."""
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    return get_case_trace(case_id)


@app.get("/cases/{case_id}/evidence")
def get_case_evidence_endpoint(case_id: str):
    """Retrieve all structured evidence items and tool results for a case."""
    case = get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail=f"Case '{case_id}' not found")
    return get_case_evidence(case_id)


# ── Milestone 7: Evaluation & Benchmark Endpoints ────────────────────


@app.get("/evaluation/cases")
def get_evaluation_cases():
    """Retrieve the 36 independent benchmark evaluation cases."""
    runner = BenchmarkRunner()
    cases, _ = runner.load_dataset()
    return cases


@app.get("/evaluation/benchmark")
def get_benchmark_results():
    """Retrieve the latest quantitative benchmark metrics across all 36 evaluation scenarios."""
    summary = execute_benchmark()
    return summary.to_dict()


@app.post("/evaluation/run")
def run_benchmark_endpoint():
    """Trigger a live re-evaluation of the 36-scenario benchmark suite."""
    summary = execute_benchmark()
    return summary.to_dict()
