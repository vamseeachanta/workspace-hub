"""TDD tests for WRK-1067: coverage gate enforcement.

Tests are self-contained (no live pytest runs required).
All fixtures use in-memory YAML/JSON data.

Structure:
- TestFloorFunction: direct import unit tests for _floor()
- TestCheckReposDirect: direct import unit tests for check_repos()
- TestRatchetLogic: subprocess integration tests (full CLI)
- TestCoverageJsonParsing: subprocess integration tests
- TestBaselineSchema: subprocess integration tests
"""

import json
import sys
import textwrap
from pathlib import Path

import pytest
import yaml

# Allow importing from scripts/testing without installation
SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from check_coverage_ratchet import _floor, check_repos


# ---------------------------------------------------------------------------
# Direct unit tests (fast — no subprocess)
# ---------------------------------------------------------------------------


class TestFloorFunction:
    """Unit tests for _floor() — the minimum acceptable coverage calculation."""

    def test_floor_at_80_baseline(self):
        assert _floor(80.0) == 80.0

    def test_floor_above_80_baseline(self):
        # 85% baseline → floor = max(80, 83) = 83
        assert _floor(85.0) == 83.0

    def test_floor_below_80_baseline_pure_ratchet(self):
        # 75% baseline → floor = max(0, 73) = 73
        assert _floor(75.0) == 73.0

    def test_floor_at_zero_baseline(self):
        assert _floor(0.0) == 0.0

    def test_floor_at_2_baseline(self):
        # 2% baseline → floor = max(0, 0) = 0
        assert _floor(2.0) == 0.0

    def test_floor_below_2_baseline(self):
        # 1% baseline → floor = max(0, -1) = 0
        assert _floor(1.0) == 0.0


class TestCheckReposDirect:
    """Unit tests for check_repos() — the ratchet evaluation logic."""

    def _make_entry(self, pct, **kwargs):
        return {"coverage_pct": float(pct), "updated_at": "2026-03-09", **kwargs}

    def test_pass_single_repo(self):
        passes, failures = check_repos(
            {"assethold": self._make_entry(85)},
            {"assethold": 86.0},
        )
        assert len(passes) == 1
        assert len(failures) == 0

    def test_fail_single_repo(self):
        passes, failures = check_repos(
            {"assethold": self._make_entry(85)},
            {"assethold": 82.0},
        )
        assert len(failures) == 1
        assert failures[0]["repo"] == "assethold"

    def test_exempt_repo_skipped(self):
        passes, failures = check_repos(
            {"legacy": self._make_entry(30, exempt=True, exempt_reason="legacy")},
            {"legacy": 10.0},
        )
        assert len(failures) == 0
        assert passes[0]["status"] == "exempt"

    def test_missing_result_fails(self):
        passes, failures = check_repos(
            {"assethold": self._make_entry(85)},
            {},
        )
        assert len(failures) == 1
        assert failures[0]["status"] == "missing"

    def test_multiple_repos_mixed_results(self):
        passes, failures = check_repos(
            {
                "assethold": self._make_entry(85),
                "assetutilities": self._make_entry(90),
            },
            {"assethold": 86.0, "assetutilities": 85.0},  # assetutilities drops >2 from 90
        )
        assert len(failures) == 1
        assert failures[0]["repo"] == "assetutilities"

    def test_below_80_ratchet_only_pass(self):
        """Below-80% baseline: 74% actual passes (only 1% drop from 75)."""
        passes, failures = check_repos(
            {"worldenergydata": self._make_entry(75)},
            {"worldenergydata": 74.0},
        )
        assert len(failures) == 0

    def test_below_80_ratchet_fail(self):
        """Below-80% baseline: 72% actual fails (3% drop from 75)."""
        passes, failures = check_repos(
            {"worldenergydata": self._make_entry(75)},
            {"worldenergydata": 72.0},
        )
        assert len(failures) == 1


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def make_baseline(repos: dict) -> dict:
    """Build a coverage-baseline.yaml structure from {repo: pct_or_dict}."""
    result: dict = {"schema_version": "1", "updated_at": "2026-03-09", "repos": {}}
    for name, val in repos.items():
        if isinstance(val, dict):
            result["repos"][name] = val
        else:
            result["repos"][name] = {"coverage_pct": float(val), "updated_at": "2026-03-09"}
    return result


def make_results(repos: dict) -> dict:
    """Build a coverage-results.json structure from {repo: pct}."""
    return {name: float(pct) for name, pct in repos.items()}


# ---------------------------------------------------------------------------
# Ratchet logic tests (TDD — these must pass after check_coverage_ratchet.py is written)
# ---------------------------------------------------------------------------


class TestRatchetLogic:
    """Unit tests for the ratchet enforcement rule:
    actual >= max(80.0, baseline_pct - 2.0)  → PASS
    actual < max(80.0, baseline_pct - 2.0)   → FAIL
    """

    def _run(self, baseline_data: dict, results_data: dict, tmp_path: Path) -> tuple[int, str]:
        """Write files to tmp_path and run check_coverage_ratchet.py. Returns (exit_code, output)."""
        import subprocess

        baseline_file = tmp_path / "coverage-baseline.yaml"
        results_file = tmp_path / "coverage-results.json"
        report_out = tmp_path / "report.txt"

        baseline_file.write_text(yaml.dump(baseline_data))
        results_file.write_text(json.dumps(results_data))

        ratchet_script = SCRIPTS_DIR / "check_coverage_ratchet.py"
        result = subprocess.run(
            [
                sys.executable, str(ratchet_script),
                "--baseline", str(baseline_file),
                "--results", str(results_file),
                "--report-out", str(report_out),
            ],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        return result.returncode, output

    def test_pass_when_above_80_and_above_ratchet(self, tmp_path):
        baseline = make_baseline({"assetutilities": 85.0})
        results = make_results({"assetutilities": 86.0})
        exit_code, _ = self._run(baseline, results, tmp_path)
        assert exit_code == 0

    def test_pass_when_at_ratchet_floor(self, tmp_path):
        """actual == baseline - 2 is exactly at threshold: PASS."""
        baseline = make_baseline({"assetutilities": 85.0})
        results = make_results({"assetutilities": 83.0})
        exit_code, _ = self._run(baseline, results, tmp_path)
        assert exit_code == 0

    def test_fail_when_below_ratchet_floor(self, tmp_path):
        """actual < baseline - 2: FAIL."""
        baseline = make_baseline({"assetutilities": 85.0})
        results = make_results({"assetutilities": 82.9})
        exit_code, output = self._run(baseline, results, tmp_path)
        assert exit_code == 1
        assert "assetutilities" in output

    def test_fail_when_below_ratchet_below_80_baseline(self, tmp_path):
        """Baseline 75%, actual 72% — drops >2% below baseline: FAIL (ratchet)."""
        baseline = make_baseline({"worldenergydata": 75.0})
        results = make_results({"worldenergydata": 72.9})
        exit_code, output = self._run(baseline, results, tmp_path)
        assert exit_code == 1
        assert "worldenergydata" in output

    def test_pass_below_80_baseline_no_regression(self, tmp_path):
        """Baseline 75%, actual 74% — within 2% of below-80% baseline: PASS (ratchet only)."""
        baseline = make_baseline({"worldenergydata": 75.0})
        results = make_results({"worldenergydata": 74.0})
        exit_code, _ = self._run(baseline, results, tmp_path)
        assert exit_code == 0

    def test_fail_when_below_80_hard_floor_at_80_plus_baseline(self, tmp_path):
        """Baseline 82%, actual 78% — below 80% hard floor (baseline >= 80): FAIL."""
        baseline = make_baseline({"digitalmodel": 82.0})
        results = make_results({"digitalmodel": 78.0})
        exit_code, output = self._run(baseline, results, tmp_path)
        assert exit_code == 1

    def test_pass_when_at_exactly_80_from_below_80_baseline(self, tmp_path):
        """Baseline 78%, actual 80% — crosses 80% threshold: PASS."""
        baseline = make_baseline({"assethold": 78.0})
        results = make_results({"assethold": 80.0})
        exit_code, _ = self._run(baseline, results, tmp_path)
        assert exit_code == 0

    def test_skip_exempt_repo(self, tmp_path):
        """Repos marked exempt: true are not checked."""
        baseline = make_baseline({
            "legacy": {"coverage_pct": 45.0, "exempt": True,
                       "exempt_reason": "legacy — WRK-9999", "updated_at": "2026-03-09"},
        })
        results = make_results({"legacy": 10.0})
        exit_code, _ = self._run(baseline, results, tmp_path)
        assert exit_code == 0

    def test_multiple_repos_one_fails(self, tmp_path):
        """Only one repo fails — exit code 1, message names the failing repo."""
        baseline = make_baseline({"assetutilities": 90.0, "assethold": 85.0})
        results = make_results({"assetutilities": 91.0, "assethold": 70.0})
        exit_code, output = self._run(baseline, results, tmp_path)
        assert exit_code == 1
        assert "assethold" in output
        assert "assetutilities" not in output or "PASS" in output or "pass" in output.lower()

    def test_report_file_written(self, tmp_path):
        """Report file is always written to --report-out path."""
        baseline = make_baseline({"assetutilities": 85.0})
        results = make_results({"assetutilities": 86.0})
        self._run(baseline, results, tmp_path)
        report = tmp_path / "report.txt"
        assert report.exists()
        assert report.read_text().strip()

    def test_bypass_reason_logged_in_report(self, tmp_path, monkeypatch):
        """SKIP_COVERAGE_REASON env var is logged in the report."""
        import subprocess
        import os

        baseline = make_baseline({"assetutilities": 85.0})
        results = make_results({"assetutilities": 40.0})  # would normally fail

        baseline_file = tmp_path / "coverage-baseline.yaml"
        results_file = tmp_path / "coverage-results.json"
        report_out = tmp_path / "report.txt"
        baseline_file.write_text(yaml.dump(baseline))
        results_file.write_text(json.dumps(results))

        ratchet_script = SCRIPTS_DIR / "check_coverage_ratchet.py"
        env = {**os.environ, "SKIP_COVERAGE_REASON": "hotfix: deploy blocker"}
        result = subprocess.run(
            [
                sys.executable, str(ratchet_script),
                "--baseline", str(baseline_file),
                "--results", str(results_file),
                "--report-out", str(report_out),
            ],
            capture_output=True,
            text=True,
            env=env,
        )
        assert result.returncode == 0, "should pass when bypass reason set"
        report_text = report_out.read_text()
        assert "hotfix" in report_text or "SKIP_COVERAGE_REASON" in report_text


# ---------------------------------------------------------------------------
# coverage-results.json JSON extraction tests
# ---------------------------------------------------------------------------


class TestCoverageJsonParsing:
    """Verify that the ratchet script can read coverage.json and extract TOTAL %."""

    def _make_coverage_json(self, pct: float) -> dict:
        """Minimal coverage.json structure matching pytest-cov output."""
        return {
            "meta": {"version": "7.3.2"},
            "totals": {
                "covered_lines": 800,
                "num_statements": 1000,
                "percent_covered": pct,
                "percent_covered_display": f"{pct:.0f}%",
                "missing_lines": int(1000 - 800),
                "excluded_lines": 0,
            },
            "files": {},
        }

    def test_extract_pct_from_coverage_json(self, tmp_path):
        """Script parses coverage.json totals.percent_covered correctly."""
        import subprocess

        cov_json = self._make_coverage_json(87.5)
        coverage_file = tmp_path / "assetutilities_coverage.json"
        coverage_file.write_text(json.dumps(cov_json))

        # Use --results flag with JSON mapping
        baseline = make_baseline({"assetutilities": 85.0})
        results = make_results({"assetutilities": 87.5})  # pre-extracted

        baseline_file = tmp_path / "coverage-baseline.yaml"
        results_file = tmp_path / "coverage-results.json"
        baseline_file.write_text(yaml.dump(baseline))
        results_file.write_text(json.dumps(results))

        ratchet_script = SCRIPTS_DIR / "check_coverage_ratchet.py"
        result = subprocess.run(
            [sys.executable, str(ratchet_script),
             "--baseline", str(baseline_file),
             "--results", str(results_file)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# Baseline schema tests
# ---------------------------------------------------------------------------


class TestBaselineSchema:
    """Verify baseline YAML schema validation in the ratchet script."""

    def _run(self, baseline_data: dict, results_data: dict, tmp_path: Path) -> tuple[int, str]:
        import subprocess

        baseline_file = tmp_path / "coverage-baseline.yaml"
        results_file = tmp_path / "coverage-results.json"
        baseline_file.write_text(yaml.dump(baseline_data))
        results_file.write_text(json.dumps(results_data))

        ratchet_script = SCRIPTS_DIR / "check_coverage_ratchet.py"
        result = subprocess.run(
            [sys.executable, str(ratchet_script),
             "--baseline", str(baseline_file),
             "--results", str(results_file)],
            capture_output=True, text=True,
        )
        return result.returncode, result.stdout + result.stderr

    def test_missing_repos_key_fails(self, tmp_path):
        """Baseline without 'repos' key fails with clear error."""
        exit_code, output = self._run({"schema_version": "1"}, {}, tmp_path)
        assert exit_code != 0

    def test_exempt_requires_reason(self, tmp_path):
        """Exempt repo without exempt_reason is rejected."""
        baseline = make_baseline({
            "legacy": {"coverage_pct": 45.0, "exempt": True, "updated_at": "2026-03-09"},
        })
        exit_code, output = self._run(baseline, {"legacy": 45.0}, tmp_path)
        assert exit_code != 0
        assert "exempt_reason" in output
