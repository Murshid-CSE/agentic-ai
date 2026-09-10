"""Top-level evaluation package proxy."""

import sys
from pathlib import Path

# Ensure backend and backend/app are on sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.evaluation import (
    BenchmarkRunner,
    BenchmarkSummary,
    CaseEvaluation,
    CategoryMetric,
    evaluate_benchmark_results,
    execute_benchmark,
    format_terminal_report,
    save_report_json,
)

__all__ = [
    "BenchmarkRunner",
    "BenchmarkSummary",
    "CaseEvaluation",
    "CategoryMetric",
    "evaluate_benchmark_results",
    "execute_benchmark",
    "format_terminal_report",
    "save_report_json",
]
