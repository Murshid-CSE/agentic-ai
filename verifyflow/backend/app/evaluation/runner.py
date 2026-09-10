"""Benchmark runner for VerifyFlow.

Loads 36 independent evaluation cases, executes them through the VerifyFlow
agent loop without polluting the primary database, and scores the results
against expected ground-truth actions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..agent.controller import run_investigation
from ..models.schemas import PaymentRequest
from .metrics import (
    BenchmarkSummary,
    CaseEvaluation,
    evaluate_benchmark_results,
)


def get_default_data_paths() -> tuple[Path, Path]:
    """Resolve absolute paths to cases.json and expected_results.json."""
    # Look in project root data/evaluation/
    base_dir = Path(__file__).resolve().parents[3]
    eval_dir = base_dir / "data" / "evaluation"
    cases_path = eval_dir / "cases.json"
    expected_path = eval_dir / "expected_results.json"
    return cases_path, expected_path


class BenchmarkRunner:
    """Orchestrates benchmark execution and result collection."""

    def __init__(
        self,
        cases_path: Path | str | None = None,
        expected_path: Path | str | None = None,
    ):
        default_cases, default_expected = get_default_data_paths()
        self.cases_path = Path(cases_path) if cases_path else default_cases
        self.expected_path = Path(expected_path) if expected_path else default_expected

    def load_dataset(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Load benchmark cases and expected results from disk."""
        if not self.cases_path.exists():
            raise FileNotFoundError(f"Benchmark cases not found at {self.cases_path}")
        if not self.expected_path.exists():
            raise FileNotFoundError(f"Expected results not found at {self.expected_path}")

        with open(self.cases_path, "r", encoding="utf-8") as f:
            cases = json.load(f)
        with open(self.expected_path, "r", encoding="utf-8") as f:
            expected = json.load(f)

        return cases, expected

    def run_case(
        self,
        case_data: dict[str, Any],
        expected_spec: dict[str, Any],
    ) -> CaseEvaluation:
        """Run an individual benchmark case and compare against expected ground truth."""
        req_dict = case_data["request"]
        try:
            payment_request = PaymentRequest(
                request_id=req_dict["request_id"],
                vendor_name=req_dict["vendor_name"],
                sender_email=req_dict["sender_email"],
                sender_domain=req_dict["sender_domain"],
                invoice_number=req_dict["invoice_number"],
                amount=req_dict["amount"],
                requested_account=req_dict["requested_account"],
                urgency=req_dict.get("urgency", "normal"),
            )
        except Exception as val_err:
            # Input trust boundary: Schema validation failures immediately fail closed to HOLD
            is_correct = "HOLD" == expected_spec["expected_action"]
            return CaseEvaluation(
                case_id=case_data["id"],
                name=case_data.get("name", case_data["id"]),
                category=case_data.get("category", "uncategorized"),
                description=case_data.get("description", ""),
                expected_action=expected_spec["expected_action"],
                actual_action="HOLD",
                is_critical_fraud=expected_spec.get("is_critical_fraud", False),
                is_action_correct=is_correct,
                is_action_safe="HOLD" in expected_spec.get("safe_actions", ["HOLD"]),
                tools_used_count=0,
                tools_used=[],
                adaptations=0,
                trace_length=1,
                risk_score=100,
                risk_level="CRITICAL",
                failures=[{"tool_name": "input_boundary", "category": "INVALID_RESULT", "detail": str(val_err)}],
                passed=is_correct,
                rationale=f"Pydantic input boundary rejection: {val_err}",
            )

        cfg = case_data.get("runtime_config", {})
        verification_available = cfg.get("verification_available", False)
        verification_verified = cfg.get("verification_verified", None)
        enable_secondary = cfg.get("enable_secondary_verification", False)
        trusted_contact_reachable = cfg.get("trusted_contact_reachable", False)
        trusted_contact_confirmed = cfg.get("trusted_contact_confirmed", None)

        # Execute investigation without database persistence
        res = run_investigation(
            payment_request,
            verification_available=verification_available,
            verification_verified=verification_verified,
            enable_secondary_verification=enable_secondary,
            trusted_contact_reachable=trusted_contact_reachable,
            trusted_contact_confirmed=trusted_contact_confirmed,
            persist=False,
        )

        actual_action = res.final_action.value
        expected_action = expected_spec["expected_action"]
        is_critical_fraud = expected_spec.get("is_critical_fraud", False)
        safe_actions = expected_spec.get("safe_actions", [expected_action])

        is_action_correct = actual_action == expected_action
        is_action_safe = actual_action in safe_actions

        tools_count = len(res.tools_used)
        min_tools = expected_spec.get("min_tools", 0)
        max_tools = expected_spec.get("max_tools", 99)
        tools_in_bounds = min_tools <= tools_count <= max_tools

        passed = is_action_correct and tools_in_bounds

        return CaseEvaluation(
            case_id=case_data["id"],
            name=case_data.get("name", case_data["id"]),
            category=case_data.get("category", "uncategorized"),
            description=case_data.get("description", ""),
            expected_action=expected_action,
            actual_action=actual_action,
            is_critical_fraud=is_critical_fraud,
            is_action_correct=is_action_correct,
            is_action_safe=is_action_safe,
            tools_used_count=tools_count,
            tools_used=res.tools_used,
            adaptations=res.adaptations,
            trace_length=len(res.trace),
            risk_score=res.risk_score,
            risk_level=res.risk_level.value,
            failures=res.failures,
            passed=passed,
            rationale=expected_spec.get("rationale", ""),
        )

    def run_benchmark(self) -> BenchmarkSummary:
        """Run all cases in the dataset and return the aggregate summary."""
        cases, expected_map = self.load_dataset()
        evaluations: list[CaseEvaluation] = []

        for case_data in cases:
            case_id = case_data["id"]
            if case_id not in expected_map:
                raise KeyError(f"No expected result defined for benchmark case '{case_id}'")
            expected_spec = expected_map[case_id]
            eval_record = self.run_case(case_data, expected_spec)
            evaluations.append(eval_record)

        # Compute comparative baselines
        from .baselines import run_oneshot_llm_baseline, run_static_pipeline_baseline
        static_baseline = run_static_pipeline_baseline(cases, expected_map)
        llm_baseline = run_oneshot_llm_baseline(cases, expected_map)
        baselines = {
            "static_pipeline": static_baseline.__dict__,
            "oneshot_llm": llm_baseline.__dict__,
        }

        return evaluate_benchmark_results(evaluations, baselines=baselines)


def execute_benchmark(
    cases_path: Path | str | None = None,
    expected_path: Path | str | None = None,
) -> BenchmarkSummary:
    """Convenience helper to run the benchmark suite and return results."""
    runner = BenchmarkRunner(cases_path=cases_path, expected_path=expected_path)
    return runner.run_benchmark()
