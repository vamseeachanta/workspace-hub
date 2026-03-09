"""Unit tests for scripts/testing/parse_pytest_output.py

Tests the parse_summary() function against all pytest exit-code paths and
output edge cases. No subprocess calls — feed fixture strings directly.

Pytest exit codes:
  0 = all tests passed
  1 = some tests failed
  2 = interrupted (Ctrl-C, timeout)
  3 = internal error
  4 = CLI usage error
  5 = no tests collected
"""

import json
import sys
from pathlib import Path

import pytest

# Make the parse_pytest_output module importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts" / "testing"))

from parse_pytest_output import parse_summary, build_record


# ── fixtures ──────────────────────────────────────────────────────────────────

NORMAL_PASS = "5 passed in 0.12s"
NORMAL_FAIL = "3 passed, 2 failed in 0.45s"
WITH_SKIP = "4 passed, 1 skipped in 0.20s"
WITH_ERROR = "2 passed, 1 error in 0.33s"
MIXED = "1 passed, 2 failed, 3 skipped, 1 error in 1.05s"
NO_SUMMARY = "ImportError while collecting test_foo.py"
EMPTY_OUTPUT = ""
XFAIL_XPASS = "3 passed, 1 xfailed, 1 xpassed in 0.55s"


# ── parse_summary tests ───────────────────────────────────────────────────────

class TestParseSummary:
    def test_normal_pass(self):
        counts = parse_summary(NORMAL_PASS)
        assert counts["passed"] == 5
        assert counts["failed"] == 0
        assert counts["error"] == 0
        assert counts["skipped"] == 0

    def test_normal_fail(self):
        counts = parse_summary(NORMAL_FAIL)
        assert counts["passed"] == 3
        assert counts["failed"] == 2

    def test_with_skip(self):
        counts = parse_summary(WITH_SKIP)
        assert counts["passed"] == 4
        assert counts["skipped"] == 1

    def test_with_error(self):
        counts = parse_summary(WITH_ERROR)
        assert counts["error"] == 1

    def test_mixed_counts(self):
        counts = parse_summary(MIXED)
        assert counts["passed"] == 1
        assert counts["failed"] == 2
        assert counts["skipped"] == 3
        assert counts["error"] == 1

    def test_no_summary_line_returns_zeros(self):
        """Collection errors produce no summary line — all counts default to 0."""
        counts = parse_summary(NO_SUMMARY)
        assert counts["passed"] == 0
        assert counts["failed"] == 0

    def test_empty_output_returns_zeros(self):
        counts = parse_summary(EMPTY_OUTPUT)
        assert counts["passed"] == 0

    def test_xfail_xpass_ignored(self):
        """xfailed/xpassed are not counted as passed or failed."""
        counts = parse_summary(XFAIL_XPASS)
        assert counts["passed"] == 3
        assert counts["failed"] == 0


# ── build_record tests ────────────────────────────────────────────────────────

EXPECTED_FAILURES = {
    "tests/test_live.py::TestLive::test_fetch_prices",
    "tests/test_live.py::TestLive::test_fetch_rates",
}


class TestBuildRecord:
    def test_exit0_all_pass(self):
        record = build_record(
            repo="myrepo",
            exit_code=0,
            raw_output=NORMAL_PASS,
            failed_node_ids=set(),
            expected_failures=set(),
        )
        assert record["status"] == "ok"
        assert record["passed"] == 5
        assert record["unexpected"] == 0
        assert record["exit_code"] == 0

    def test_exit1_unexpected_failures(self):
        raw = "3 passed, 2 failed in 0.5s"
        failed = {"tests/test_foo.py::test_a", "tests/test_foo.py::test_b"}
        record = build_record(
            repo="myrepo",
            exit_code=1,
            raw_output=raw,
            failed_node_ids=failed,
            expected_failures=set(),
        )
        assert record["status"] == "unexpected_failures"
        assert record["failed"] == 2
        assert record["unexpected"] == 2
        assert record["expected_fail"] == 0

    def test_exit1_all_expected(self):
        """All failures are in expected set → status ok, unexpected=0."""
        raw = "3 passed, 2 failed in 0.5s"
        failed = {
            "tests/test_live.py::TestLive::test_fetch_prices",
            "tests/test_live.py::TestLive::test_fetch_rates",
        }
        record = build_record(
            repo="myrepo",
            exit_code=1,
            raw_output=raw,
            failed_node_ids=failed,
            expected_failures=EXPECTED_FAILURES,
        )
        assert record["status"] == "ok"
        assert record["unexpected"] == 0
        assert record["expected_fail"] == 2

    def test_exit1_mixed_expected_unexpected(self):
        raw = "2 passed, 3 failed in 0.5s"
        failed = {
            "tests/test_live.py::TestLive::test_fetch_prices",  # expected
            "tests/test_foo.py::test_new_failure",              # unexpected
            "tests/test_bar.py::test_other",                    # unexpected
        }
        record = build_record(
            repo="myrepo",
            exit_code=1,
            raw_output=raw,
            failed_node_ids=failed,
            expected_failures=EXPECTED_FAILURES,
        )
        assert record["status"] == "unexpected_failures"
        assert record["unexpected"] == 2
        assert record["expected_fail"] == 1

    def test_exit2_interrupted(self):
        record = build_record(
            repo="myrepo",
            exit_code=2,
            raw_output="",
            failed_node_ids=set(),
            expected_failures=set(),
        )
        assert record["status"] == "error"
        assert record["exit_code"] == 2

    def test_exit3_internal_error(self):
        record = build_record(
            repo="myrepo",
            exit_code=3,
            raw_output="",
            failed_node_ids=set(),
            expected_failures=set(),
        )
        assert record["status"] == "error"

    def test_exit4_cli_error(self):
        record = build_record(
            repo="myrepo",
            exit_code=4,
            raw_output="",
            failed_node_ids=set(),
            expected_failures=set(),
        )
        assert record["status"] == "error"

    def test_exit5_no_tests_collected(self):
        record = build_record(
            repo="myrepo",
            exit_code=5,
            raw_output="no tests ran",
            failed_node_ids=set(),
            expected_failures=set(),
        )
        assert record["status"] == "no_tests"
        assert record["passed"] == 0

    def test_record_contains_repo_name(self):
        record = build_record(
            repo="assetutilities",
            exit_code=0,
            raw_output=NORMAL_PASS,
            failed_node_ids=set(),
            expected_failures=set(),
        )
        assert record["repo"] == "assetutilities"

    def test_record_is_json_serialisable(self):
        record = build_record(
            repo="myrepo",
            exit_code=0,
            raw_output=NORMAL_PASS,
            failed_node_ids=set(),
            expected_failures=set(),
        )
        json.dumps(record)  # must not raise

    def test_skipped_only_exit0(self):
        """All tests skipped — exit code 0, status ok."""
        raw = "5 skipped in 0.05s"
        record = build_record(
            repo="myrepo",
            exit_code=0,
            raw_output=raw,
            failed_node_ids=set(),
            expected_failures=set(),
        )
        assert record["status"] == "ok"
        assert record["skipped"] == 5
        assert record["passed"] == 0

    def test_collection_error_no_summary(self):
        """ImportError during collection — no summary line, exit code 2."""
        record = build_record(
            repo="myrepo",
            exit_code=2,
            raw_output="ImportError while collecting tests/test_broken.py",
            failed_node_ids=set(),
            expected_failures=set(),
        )
        assert record["status"] == "error"
        assert record["passed"] == 0
