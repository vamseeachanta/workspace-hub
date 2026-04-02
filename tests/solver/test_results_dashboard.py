"""Tests for solver results dashboard generation.

ABOUTME: Validates results_dashboard.py — JSONL parsing, summary generation,
time-series aggregation, and markdown report output.
All filesystem operations use temp directories.
"""
from __future__ import annotations

import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'solver'))
from results_dashboard import (
    DashboardSummary,
    JobResult,
    generate_markdown_report,
    generate_summary,
    parse_results_log,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_jsonl(path: Path, entries: list[dict]) -> Path:
    """Write a list of dicts as JSONL."""
    with open(path, "w") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    return path


SAMPLE_ENTRIES = [
    {
        "status": "completed",
        "solver": "orcawave",
        "input_file": "test01.owd",
        "processed_at": "2026-04-01T10:00:00Z",
        "elapsed_seconds": 12.5,
        "job_dir": "20260401T100000Z-test01",
    },
    {
        "status": "completed",
        "solver": "orcaflex",
        "input_file": "riser_A01.dat",
        "processed_at": "2026-04-01T14:30:00Z",
        "elapsed_seconds": 45.2,
        "job_dir": "20260401T143000Z-riser",
    },
    {
        "status": "failed",
        "solver": "orcawave",
        "input_file": "broken.owd",
        "processed_at": "2026-04-02T08:00:00Z",
        "elapsed_seconds": 1.1,
        "error": "License check failed",
        "job_dir": "20260402T080000Z-broken",
    },
    {
        "status": "completed",
        "solver": "orcawave",
        "input_file": "test02.owd",
        "processed_at": "2026-04-02T09:00:00Z",
        "elapsed_seconds": 18.3,
        "job_dir": "20260402T090000Z-test02",
    },
]


# ---------------------------------------------------------------------------
# Tests: JSONL Parsing
# ---------------------------------------------------------------------------

class TestParseResultsLog:
    """Test JSONL parsing from results log."""

    def test_parses_valid_jsonl(self, tmp_path: Path):
        """Valid JSONL produces correct number of JobResult objects."""
        log = make_jsonl(tmp_path / "results.jsonl", SAMPLE_ENTRIES)
        results = parse_results_log(log)
        assert len(results) == 4
        assert all(isinstance(r, JobResult) for r in results)

    def test_skips_blank_lines(self, tmp_path: Path):
        """Blank lines in JSONL are skipped gracefully."""
        log = tmp_path / "results.jsonl"
        log.write_text(
            json.dumps(SAMPLE_ENTRIES[0]) + "\n\n"
            + json.dumps(SAMPLE_ENTRIES[1]) + "\n"
        )
        results = parse_results_log(log)
        assert len(results) == 2

    def test_skips_malformed_lines(self, tmp_path: Path):
        """Malformed JSON lines are skipped without raising."""
        log = tmp_path / "results.jsonl"
        log.write_text(
            json.dumps(SAMPLE_ENTRIES[0]) + "\n"
            + "NOT VALID JSON\n"
            + json.dumps(SAMPLE_ENTRIES[1]) + "\n"
        )
        results = parse_results_log(log)
        assert len(results) == 2

    def test_empty_file(self, tmp_path: Path):
        """Empty JSONL file returns empty list."""
        log = tmp_path / "results.jsonl"
        log.write_text("")
        results = parse_results_log(log)
        assert results == []

    def test_nonexistent_file(self, tmp_path: Path):
        """Non-existent file returns empty list."""
        results = parse_results_log(tmp_path / "nope.jsonl")
        assert results == []


# ---------------------------------------------------------------------------
# Tests: Summary Generation
# ---------------------------------------------------------------------------

class TestGenerateSummary:
    """Test dashboard summary aggregation."""

    def test_total_count(self, tmp_path: Path):
        """Summary total matches input count."""
        log = make_jsonl(tmp_path / "results.jsonl", SAMPLE_ENTRIES)
        results = parse_results_log(log)
        summary = generate_summary(results)
        assert summary.total == 4

    def test_pass_fail_counts(self, tmp_path: Path):
        """Summary correctly counts pass/fail."""
        log = make_jsonl(tmp_path / "results.jsonl", SAMPLE_ENTRIES)
        results = parse_results_log(log)
        summary = generate_summary(results)
        assert summary.passed == 3
        assert summary.failed == 1

    def test_pending_count(self, tmp_path: Path):
        """Summary counts pending jobs."""
        entries = SAMPLE_ENTRIES + [
            {"status": "pending", "solver": "orcawave", "input_file": "p.owd",
             "processed_at": "", "elapsed_seconds": 0, "job_dir": "pending-1"},
        ]
        log = make_jsonl(tmp_path / "results.jsonl", entries)
        results = parse_results_log(log)
        summary = generate_summary(results)
        assert summary.pending == 1

    def test_empty_results(self):
        """Empty results produce zero summary."""
        summary = generate_summary([])
        assert summary.total == 0
        assert summary.passed == 0
        assert summary.failed == 0


# ---------------------------------------------------------------------------
# Tests: Time-series aggregation
# ---------------------------------------------------------------------------

class TestTimeSeries:
    """Test time-series aggregation (jobs per day)."""

    def test_jobs_per_day(self, tmp_path: Path):
        """Summary groups jobs by date."""
        log = make_jsonl(tmp_path / "results.jsonl", SAMPLE_ENTRIES)
        results = parse_results_log(log)
        summary = generate_summary(results)
        # 2 jobs on 2026-04-01, 2 jobs on 2026-04-02
        assert summary.jobs_per_day.get("2026-04-01") == 2
        assert summary.jobs_per_day.get("2026-04-02") == 2


# ---------------------------------------------------------------------------
# Tests: Markdown report generation
# ---------------------------------------------------------------------------

class TestMarkdownReport:
    """Test markdown dashboard report."""

    def test_report_has_header(self, tmp_path: Path):
        """Report starts with a dashboard title."""
        log = make_jsonl(tmp_path / "results.jsonl", SAMPLE_ENTRIES)
        results = parse_results_log(log)
        summary = generate_summary(results)
        report = generate_markdown_report(summary)
        assert "# Solver Queue Dashboard" in report

    def test_report_has_summary_table(self, tmp_path: Path):
        """Report contains a summary section with counts."""
        log = make_jsonl(tmp_path / "results.jsonl", SAMPLE_ENTRIES)
        results = parse_results_log(log)
        summary = generate_summary(results)
        report = generate_markdown_report(summary)
        assert "Total" in report
        assert "Passed" in report or "Completed" in report
        assert "Failed" in report

    def test_report_has_daily_breakdown(self, tmp_path: Path):
        """Report contains a daily job count breakdown."""
        log = make_jsonl(tmp_path / "results.jsonl", SAMPLE_ENTRIES)
        results = parse_results_log(log)
        summary = generate_summary(results)
        report = generate_markdown_report(summary)
        assert "2026-04-01" in report
        assert "2026-04-02" in report

    def test_empty_report(self):
        """Empty summary generates a report with zero counts."""
        summary = generate_summary([])
        report = generate_markdown_report(summary)
        assert "0" in report
