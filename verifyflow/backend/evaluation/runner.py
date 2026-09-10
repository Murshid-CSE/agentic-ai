"""CLI entry point for running the VerifyFlow evaluation benchmark suite.

Usage:
    python -m backend.evaluation.runner
    python -m app.evaluation.runner
"""

import sys
from pathlib import Path

# Ensure paths are set
project_root = Path(__file__).resolve().parents[2]
backend_dir = project_root / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app.evaluation.report import format_terminal_report, save_report_json
from app.evaluation.runner import BenchmarkRunner


def main() -> int:
    """Run VerifyFlow benchmark suite and print terminal report."""
    runner = BenchmarkRunner()
    summary = runner.run_benchmark()

    # Print formatted report
    report_text = format_terminal_report(summary)
    print(report_text)

    # Save artifact to data/evaluation/benchmark_report.json
    report_path = project_root / "data" / "evaluation" / "benchmark_report.json"
    save_report_json(summary, report_path)
    print(f"\n[Artifact Saved] JSON report written to: {report_path}")

    # Return exit code based on critical safety invariant
    if summary.critical_false_approvals > 0:
        print("\n[CRITICAL FAILURE] Security invariant violated: critical cases approved!")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
