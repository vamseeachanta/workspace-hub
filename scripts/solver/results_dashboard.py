#!/usr/bin/env python3
"""Solver queue results dashboard -- JSONL log to summary + markdown report.

ABOUTME: Parses data/solver-results-log.jsonl (written by post-process-hook.py),
generates summary statistics (total/pass/fail/pending, jobs per day),
and writes a markdown dashboard to docs/solver/queue-dashboard.md.

Usage:
    uv run python scripts/solver/results_dashboard.py
    uv run python scripts/solver/results_dashboard.py --log data/solver-results-log.jsonl
    uv run python scripts/solver/results_dashboard.py --output docs/solver/queue-dashboard.md
"""
from __future__ import annotations

import datetime
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class JobResult:
    """A single solver job result parsed from JSONL.

    Attributes:
        status: Job outcome (completed, failed, pending).
        solver: Solver type used (orcawave, orcaflex).
        input_file: Path to the input model file.
        processed_at: ISO timestamp when job was processed.
        elapsed_seconds: Runtime in seconds.
        job_dir: Directory name for this job.
        error: Error message (if failed).
    """
    status: str = ""
    solver: str = ""
    input_file: str = ""
    processed_at: str = ""
    elapsed_seconds: float = 0.0
    job_dir: str = ""
    error: str = ""


@dataclass
class DashboardSummary:
    """Aggregated dashboard statistics.

    Attributes:
        total: Total number of jobs.
        passed: Number of completed/passed jobs.
        failed: Number of failed jobs.
        pending: Number of pending jobs.
        jobs_per_day: Dict mapping date string to count.
        avg_elapsed: Average elapsed seconds for completed jobs.
        solver_counts: Dict mapping solver name to count.
        generated_at: Timestamp when summary was generated.
    """
    total: int = 0
    passed: int = 0
    failed: int = 0
    pending: int = 0
    jobs_per_day: dict[str, int] = field(default_factory=dict)
    avg_elapsed: float = 0.0
    solver_counts: dict[str, int] = field(default_factory=dict)
    generated_at: str = ""


# ---------------------------------------------------------------------------
# JSONL parsing
# ---------------------------------------------------------------------------

def parse_results_log(jsonl_path: Path) -> list[JobResult]:
    """Parse solver results from a JSONL log file.

    Each line is a JSON object written by post-process-hook.py.
    Skips blank lines and malformed JSON gracefully.

    Args:
        jsonl_path: Path to the JSONL log file.

    Returns:
        List of JobResult objects.
    """
    results: list[JobResult] = []

    if not jsonl_path.exists():
        return results

    with open(jsonl_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                result = JobResult(
                    status=data.get("status", ""),
                    solver=data.get("solver", ""),
                    input_file=data.get("input_file", ""),
                    processed_at=data.get("processed_at", ""),
                    elapsed_seconds=float(data.get("elapsed_seconds", 0.0)),
                    job_dir=data.get("job_dir", ""),
                    error=data.get("error", ""),
                )
                results.append(result)
            except (json.JSONDecodeError, ValueError, TypeError):
                # Skip malformed lines
                continue

    return results


# ---------------------------------------------------------------------------
# Summary generation
# ---------------------------------------------------------------------------

def generate_summary(results: list[JobResult]) -> DashboardSummary:
    """Generate dashboard summary from parsed job results.

    Args:
        results: List of JobResult objects.

    Returns:
        DashboardSummary with aggregated stats.
    """
    summary = DashboardSummary(
        generated_at=datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
    )

    summary.total = len(results)

    # Count by status
    completed_times: list[float] = []
    solver_counter: Counter[str] = Counter()
    day_counter: Counter[str] = Counter()

    for r in results:
        status = r.status.lower()
        if status in ("completed", "passed"):
            summary.passed += 1
            completed_times.append(r.elapsed_seconds)
        elif status == "failed":
            summary.failed += 1
        elif status == "pending":
            summary.pending += 1

        # Solver counts
        if r.solver:
            solver_counter[r.solver] += 1

        # Jobs per day -- extract date from processed_at
        if r.processed_at:
            try:
                day = r.processed_at[:10]  # "2026-04-01"
                if len(day) == 10 and day[4] == "-":
                    day_counter[day] += 1
            except (IndexError, ValueError):
                pass

    # Average elapsed for completed jobs
    if completed_times:
        summary.avg_elapsed = round(sum(completed_times) / len(completed_times), 1)

    summary.solver_counts = dict(solver_counter)
    summary.jobs_per_day = dict(sorted(day_counter.items()))

    return summary


# ---------------------------------------------------------------------------
# Markdown report generation
# ---------------------------------------------------------------------------

def generate_markdown_report(summary: DashboardSummary) -> str:
    """Generate a markdown dashboard report from summary stats.

    Args:
        summary: DashboardSummary with aggregated stats.

    Returns:
        Markdown string for the dashboard file.
    """
    lines: list[str] = []

    lines.append("# Solver Queue Dashboard")
    lines.append("")
    lines.append(f"> Generated: {summary.generated_at}")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    lines.append(f"| Total | {summary.total} |")
    lines.append(f"| Completed | {summary.passed} |")
    lines.append(f"| Failed | {summary.failed} |")
    lines.append(f"| Pending | {summary.pending} |")
    lines.append(f"| Avg Elapsed (s) | {summary.avg_elapsed} |")
    lines.append("")

    # Solver breakdown
    if summary.solver_counts:
        lines.append("## Solver Breakdown")
        lines.append("")
        lines.append("| Solver | Jobs |")
        lines.append("|--------|------|")
        for solver, count in sorted(summary.solver_counts.items()):
            lines.append(f"| {solver} | {count} |")
        lines.append("")

    # Daily breakdown
    if summary.jobs_per_day:
        lines.append("## Daily Job Count")
        lines.append("")
        lines.append("| Date | Jobs |")
        lines.append("|------|------|")
        for day, count in summary.jobs_per_day.items():
            lines.append(f"| {day} | {count} |")
        lines.append("")

    # Pass rate
    if summary.total > 0:
        rate = (summary.passed / summary.total) * 100
        lines.append("## Pass Rate")
        lines.append("")
        lines.append(f"**{rate:.1f}%** ({summary.passed}/{summary.total})")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append(
        "*Auto-generated by `scripts/solver/results_dashboard.py`. "
        "Do not edit manually.*"
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_LOG = REPO_ROOT / "data" / "solver-results-log.jsonl"
DEFAULT_OUTPUT = REPO_ROOT / "docs" / "solver" / "queue-dashboard.md"


def main() -> int:
    """CLI entry point for dashboard generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate solver queue dashboard from JSONL results log."
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=DEFAULT_LOG,
        help=f"Path to JSONL results log (default: {DEFAULT_LOG})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Path to output markdown file (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    print(f"Reading: {args.log}")
    results = parse_results_log(args.log)
    print(f"Parsed {len(results)} job results")

    summary = generate_summary(results)
    print(
        f"Summary: {summary.passed} passed, {summary.failed} failed, "
        f"{summary.pending} pending out of {summary.total} total"
    )

    report = generate_markdown_report(summary)

    # Write output
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report)
    print(f"Dashboard written: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
