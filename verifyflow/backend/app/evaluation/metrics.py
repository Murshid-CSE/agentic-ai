"""Benchmark metrics calculation engine for VerifyFlow.

Security principles:
- Ground truth remains completely independent of the agent implementation.
- Critical False Approvals (approving critical fraud) has mandatory zero tolerance.
- Critical Decision Safety is measured separately from overall decision accuracy.
- Risk scores are reported as 'Risk Policy Scores', not fraud probabilities.
- A 2x2 confusion matrix separates false approvals from false positives (unnecessary holds).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ConfusionMatrix:
    """2x2 Confusion Matrix for payment decision classification."""

    true_positives: int = 0  # Expected: APPROVE, Actual: APPROVE
    true_negatives: int = 0  # Expected: HOLD/REVIEW, Actual: HOLD/REVIEW
    false_positives: int = 0  # Expected: APPROVE, Actual: HOLD/REVIEW (Unnecessary Holds / False Blocks)
    false_negatives: int = 0  # Expected: HOLD/REVIEW, Actual: APPROVE (Unsafe False Approvals - MUST BE 0)
    false_positive_rate_percent: float = 0.0
    false_approval_rate_percent: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CaseEvaluation:
    """Evaluation record for an individual benchmark scenario."""

    case_id: str
    name: str
    category: str
    description: str
    expected_action: str
    actual_action: str
    is_critical_fraud: bool
    is_action_correct: bool
    is_action_safe: bool
    tools_used_count: int
    tools_used: list[str]
    adaptations: int
    trace_length: int
    risk_score: int
    risk_level: str
    failures: list[dict[str, Any]]
    passed: bool
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CategoryMetric:
    """Aggregated performance metrics for a specific scenario category."""

    category: str
    total_cases: int = 0
    correct_actions: int = 0
    accuracy_percent: float = 0.0
    critical_cases: int = 0
    critical_false_approvals: int = 0
    critical_safety_percent: float = 100.0
    avg_tools_used: float = 0.0
    avg_adaptations: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkSummary:
    """Comprehensive benchmark results across all evaluated scenarios."""

    total_cases: int
    correct_decisions: int
    decision_accuracy_percent: float
    critical_cases_count: int
    critical_false_approvals: int
    critical_decision_safety_percent: float
    adaptation_evaluated_cases: int
    adaptation_successes: int
    adaptation_resilience_percent: float
    productive_adaptations_count: int
    safe_escalations_count: int
    avg_tools_per_case: float
    avg_adaptations_per_case: float
    avg_trace_steps: float
    max_trace_steps: int
    confusion_matrix: ConfusionMatrix
    category_metrics: dict[str, CategoryMetric]
    case_evaluations: list[CaseEvaluation] = field(default_factory=list)
    baselines: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_cases": self.total_cases,
            "correct_decisions": self.correct_decisions,
            "decision_accuracy_percent": self.decision_accuracy_percent,
            "critical_cases_count": self.critical_cases_count,
            "critical_false_approvals": self.critical_false_approvals,
            "critical_decision_safety_percent": self.critical_decision_safety_percent,
            "adaptation_evaluated_cases": self.adaptation_evaluated_cases,
            "adaptation_successes": self.adaptation_successes,
            "adaptation_resilience_percent": self.adaptation_resilience_percent,
            "productive_adaptations_count": self.productive_adaptations_count,
            "safe_escalations_count": self.safe_escalations_count,
            "avg_tools_per_case": self.avg_tools_per_case,
            "avg_adaptations_per_case": self.avg_adaptations_per_case,
            "avg_trace_steps": self.avg_trace_steps,
            "max_trace_steps": self.max_trace_steps,
            "confusion_matrix": self.confusion_matrix.to_dict(),
            "category_metrics": {k: v.to_dict() for k, v in self.category_metrics.items()},
            "case_evaluations": [c.to_dict() for c in self.case_evaluations],
            "baselines": self.baselines,
        }


def evaluate_benchmark_results(
    evaluations: list[CaseEvaluation],
    baselines: dict[str, Any] | None = None,
) -> BenchmarkSummary:
    """Aggregate a list of case evaluations into a formal benchmark summary."""
    total_cases = len(evaluations)
    if total_cases == 0:
        return BenchmarkSummary(
            total_cases=0,
            correct_decisions=0,
            decision_accuracy_percent=0.0,
            critical_cases_count=0,
            critical_false_approvals=0,
            critical_decision_safety_percent=100.0,
            adaptation_evaluated_cases=0,
            adaptation_successes=0,
            adaptation_resilience_percent=100.0,
            productive_adaptations_count=0,
            safe_escalations_count=0,
            avg_tools_per_case=0.0,
            avg_adaptations_per_case=0.0,
            avg_trace_steps=0.0,
            max_trace_steps=0,
            confusion_matrix=ConfusionMatrix(),
            category_metrics={},
            case_evaluations=[],
            baselines=baselines or {},
        )

    correct_decisions = sum(1 for c in evaluations if c.is_action_correct)
    decision_accuracy = round((correct_decisions / total_cases) * 100.0, 2)

    # ── Confusion Matrix ─────────────────────────────────────────────
    # Class: APPROVE (Positive) vs HOLD / HUMAN_REVIEW (Negative)
    tp = sum(1 for c in evaluations if c.expected_action == "APPROVE" and c.actual_action == "APPROVE")
    tn = sum(1 for c in evaluations if c.expected_action != "APPROVE" and c.actual_action != "APPROVE")
    fp = sum(1 for c in evaluations if c.expected_action == "APPROVE" and c.actual_action != "APPROVE")  # Unnecessary hold
    fn = sum(1 for c in evaluations if c.expected_action != "APPROVE" and c.actual_action == "APPROVE")  # False approval!

    fp_rate = round((fp / (tp + fp) * 100.0), 2) if (tp + fp) > 0 else 0.0
    fn_rate = round((fn / (tn + fn) * 100.0), 2) if (tn + fn) > 0 else 0.0

    cm = ConfusionMatrix(
        true_positives=tp,
        true_negatives=tn,
        false_positives=fp,
        false_negatives=fn,
        false_positive_rate_percent=fp_rate,
        false_approval_rate_percent=fn_rate,
    )

    # Critical Fraud & Decision Safety
    critical_cases = [c for c in evaluations if c.is_critical_fraud]
    critical_cases_count = len(critical_cases)
    critical_false_approvals = sum(
        1 for c in critical_cases if c.actual_action == "APPROVE"
    )
    if critical_cases_count > 0:
        safe_critical_decisions = sum(1 for c in critical_cases if c.is_action_safe)
        critical_decision_safety = round(
            (safe_critical_decisions / critical_cases_count) * 100.0, 2
        )
    else:
        critical_decision_safety = 100.0

    # Adaptation Resilience & Productive Adaptation
    adaptation_cases = [
        c
        for c in evaluations
        if c.adaptations > 0 or len(c.failures) > 0 or c.category in ("verification_failure", "conflicting_evidence")
    ]
    adaptation_evaluated_count = len(adaptation_cases)
    if adaptation_evaluated_count > 0:
        adaptation_successes = sum(
            1 for c in adaptation_cases if c.is_action_correct and c.is_action_safe
        )
        adaptation_resilience = round(
            (adaptation_successes / adaptation_evaluated_count) * 100.0, 2
        )
    else:
        adaptation_successes = 0
        adaptation_resilience = 100.0

    # Productive adaptation: Cases where alternative channel verified update -> APPROVE
    productive_count = sum(
        1 for c in adaptation_cases if c.actual_action == "APPROVE" and c.is_action_correct
    )
    # Safe escalation: Cases safely escalated to HUMAN_REVIEW or HOLD
    safe_escalation_count = sum(
        1 for c in adaptation_cases if c.actual_action in ("HOLD", "HUMAN_REVIEW") and c.is_action_safe
    )

    # Efficiency & Depth
    avg_tools = round(sum(c.tools_used_count for c in evaluations) / total_cases, 2)
    avg_adapt = round(sum(c.adaptations for c in evaluations) / total_cases, 2)
    avg_trace = round(sum(c.trace_length for c in evaluations) / total_cases, 2)
    max_trace = max((c.trace_length for c in evaluations), default=0)

    # Category Breakdown
    cat_map: dict[str, list[CaseEvaluation]] = {}
    for c in evaluations:
        cat_map.setdefault(c.category, []).append(c)

    category_metrics: dict[str, CategoryMetric] = {}
    for cat_name, cat_cases in cat_map.items():
        c_total = len(cat_cases)
        c_correct = sum(1 for c in cat_cases if c.is_action_correct)
        c_accuracy = round((c_correct / c_total) * 100.0, 2)
        c_critical = sum(1 for c in cat_cases if c.is_critical_fraud)
        c_false_appr = sum(
            1 for c in cat_cases if c.is_critical_fraud and c.actual_action == "APPROVE"
        )
        c_safe = (
            round(((c_critical - c_false_appr) / c_critical) * 100.0, 2)
            if c_critical > 0
            else 100.0
        )
        c_avg_tools = round(sum(c.tools_used_count for c in cat_cases) / c_total, 2)
        c_avg_adapt = round(sum(c.adaptations for c in cat_cases) / c_total, 2)

        category_metrics[cat_name] = CategoryMetric(
            category=cat_name,
            total_cases=c_total,
            correct_actions=c_correct,
            accuracy_percent=c_accuracy,
            critical_cases=c_critical,
            critical_false_approvals=c_false_appr,
            critical_safety_percent=c_safe,
            avg_tools_used=c_avg_tools,
            avg_adaptations=c_avg_adapt,
        )

    return BenchmarkSummary(
        total_cases=total_cases,
        correct_decisions=correct_decisions,
        decision_accuracy_percent=decision_accuracy,
        critical_cases_count=critical_cases_count,
        critical_false_approvals=critical_false_approvals,
        critical_decision_safety_percent=critical_decision_safety,
        adaptation_evaluated_cases=adaptation_evaluated_count,
        adaptation_successes=adaptation_successes,
        adaptation_resilience_percent=adaptation_resilience,
        productive_adaptations_count=productive_count,
        safe_escalations_count=safe_escalation_count,
        avg_tools_per_case=avg_tools,
        avg_adaptations_per_case=avg_adapt,
        avg_trace_steps=avg_trace,
        max_trace_steps=max_trace,
        confusion_matrix=cm,
        category_metrics=category_metrics,
        case_evaluations=evaluations,
        baselines=baselines or {},
    )
