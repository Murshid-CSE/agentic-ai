"""Tests for Milestone 7: Independent Evaluation, Benchmarking & Safety Invariants."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

from app.evaluation.metrics import (
    BenchmarkSummary,
    CaseEvaluation,
    evaluate_benchmark_results,
)
from app.evaluation.report import format_terminal_report, save_report_json
from app.evaluation.runner import BenchmarkRunner, execute_benchmark
from app.main import app

client = TestClient(app)


# ── Test 1: Dataset Integrity & Independent Ground Truth ─────────────


def test_benchmark_dataset_integrity():
    """Verify dataset contains 36 well-formed scenarios with independent ground truth."""
    runner = BenchmarkRunner()
    cases, expected = runner.load_dataset()

    assert len(cases) == 52, f"Expected 52 benchmark cases, got {len(cases)}"
    assert len(expected) == 52, f"Expected 52 ground truth expectations, got {len(expected)}"

    categories = set()
    for case in cases:
        cid = case["id"]
        assert cid in expected, f"Case '{cid}' missing from expected_results.json"
        assert "name" in case
        assert "category" in case
        assert "request" in case
        req = case["request"]
        assert "vendor_name" in req
        assert "amount" in req
        assert "requested_account" in req
        assert "sender_domain" in req
        categories.add(case["category"])

        exp = expected[cid]
        assert "expected_action" in exp
        assert "is_critical_fraud" in exp
        assert "safe_actions" in exp
        assert "min_tools" in exp
        assert "max_tools" in exp
        assert "requires_adaptation" in exp
        assert "rationale" in exp

    # Ensure required categories are covered
    expected_categories = {
        "clean_payment",
        "account_changed",
        "domain_spoof",
        "unknown_vendor",
        "unusual_amount",
        "urgent_request",
        "conflicting_evidence",
        "verification_failure",
        "adversarial_legitimate",
        "hero_critical",
    }
    assert expected_categories.issubset(categories)


# ── Test 2: Mandatory Security Invariant — Zero Critical False Approvals ─


def test_zero_critical_false_approvals_invariant():
    """INVIOLABLE SECURITY REQUIREMENT:
    Critical cases must NEVER result in automated APPROVE.
    Critical false approvals must be strictly 0 (100% Critical Decision Safety).
    """
    summary = execute_benchmark()

    # Absolute zero tolerance
    assert summary.critical_false_approvals == 0, (
        f"SECURITY BREACH: {summary.critical_false_approvals} critical fraud "
        "cases were incorrectly approved!"
    )
    assert summary.critical_decision_safety_percent == 100.0
    assert summary.critical_cases_count >= 15


# ── Test 3: Decision Accuracy on Independent Benchmark ───────────────


def test_benchmark_decision_accuracy():
    """VerifyFlow decision accuracy must be strictly verified against pre-defined ground truth."""
    summary = execute_benchmark()

    assert summary.total_cases == 52
    assert summary.correct_decisions == 52
    assert summary.decision_accuracy_percent == 100.0


# ── Test 4: Tool Selection Efficiency & Pruning Behavior ─────────────


def test_tool_selection_efficiency():
    """Verify the agent dynamically prunes checks rather than blindly running every tool."""
    summary = execute_benchmark()

    # Unknown vendor cases stop early at tool 2
    unknown_metric = summary.category_metrics["unknown_vendor"]
    assert unknown_metric.avg_tools_used == 2.0, (
        f"Unknown vendor should stop early at 2 tools, got {unknown_metric.avg_tools_used}"
    )

    # Clean payment cases run standard baseline of 4 tools
    clean_metric = summary.category_metrics["clean_payment"]
    assert clean_metric.avg_tools_used == 4.0

    # Complex / verification recovery cases execute deeper investigation (5-6 tools)
    recov_metric = summary.category_metrics["verification_failure"]
    assert recov_metric.avg_tools_used == 6.0

    # Average tools per case across entire benchmark should be between 3.5 and 5.0
    assert 3.5 <= summary.avg_tools_per_case <= 5.0


# ── Test 5: Adaptation Resilience on Failures & Ambiguity ─────────────


def test_adaptation_resilience():
    """Verify that failure-injected and ambiguous cases successfully adapt to safe outcomes."""
    summary = execute_benchmark()

    assert summary.adaptation_evaluated_cases >= 15
    assert summary.adaptation_resilience_percent == 100.0
    assert summary.adaptation_successes == summary.adaptation_evaluated_cases


# ── Test 6: Adversarial-But-Legitimate Discrimination ─────────────────


def test_adversarial_but_legitimate_discrimination():
    """Verify that unusual amounts and urgency do not cause false-positive lockouts
    when all vendor credentials match trusted records."""
    summary = execute_benchmark()

    adv_metric = summary.category_metrics["adversarial_legitimate"]
    assert adv_metric.accuracy_percent == 100.0

    unusual_metric = summary.category_metrics["unusual_amount"]
    assert unusual_metric.accuracy_percent == 100.0

    urgent_metric = summary.category_metrics["urgent_request"]
    assert urgent_metric.accuracy_percent == 100.0


# ── Test 7: Terminal & JSON Report Generation ─────────────────────────


def test_benchmark_reporting():
    """Verify terminal formatting and JSON report serialization."""
    summary = execute_benchmark()
    report = format_terminal_report(summary)

    assert "VERIFYFLOW BENCHMARK REPORT" in report
    assert "Decision Accuracy:" in report
    assert "Critical False Approvals:            0 [PASS - ZERO TOLERANCE MET]" in report
    assert "CATEGORY PERFORMANCE BREAKDOWN:" in report

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "report.json"
        save_report_json(summary, json_path)
        assert json_path.exists()
        content = json_path.read_text(encoding="utf-8")
        assert '"critical_false_approvals": 0' in content
        assert '"decision_accuracy_percent": 100.0' in content


# ── Test 8: Evaluation API Endpoints ─────────────────────────────────


def test_evaluation_api_endpoints():
    """Verify FastAPI GET /evaluation/cases, GET /evaluation/benchmark, POST /evaluation/run."""
    # 1. Cases list
    res_cases = client.get("/evaluation/cases")
    assert res_cases.status_code == 200
    cases_data = res_cases.json()
    assert len(cases_data) == 52

    # 2. Benchmark GET
    res_bench = client.get("/evaluation/benchmark")
    assert res_bench.status_code == 200
    bench_data = res_bench.json()
    assert bench_data["total_cases"] == 52
    assert bench_data["critical_false_approvals"] == 0
    assert bench_data["decision_accuracy_percent"] == 100.0

    # 3. Benchmark POST
    res_run = client.post("/evaluation/run")
    assert res_run.status_code == 200
    run_data = res_run.json()
    assert run_data["total_cases"] == 52
    assert run_data["critical_decision_safety_percent"] == 100.0
