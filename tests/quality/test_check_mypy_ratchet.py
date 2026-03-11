"""TDD tests for scripts/quality/check_mypy_ratchet.py (WRK-1092).

All tests written BEFORE implementation (RED phase).
Tests cover: schema validation, output parsing, ratchet logic, bypass, and --init mode.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

# ---------------------------------------------------------------------------
# Script under test
# ---------------------------------------------------------------------------
SCRIPT = Path(__file__).parents[2] / "scripts" / "quality" / "check_mypy_ratchet.py"

# ---------------------------------------------------------------------------
# Import helper — import the module under test for unit-level tests
# ---------------------------------------------------------------------------


def _import_module():
    """Dynamically import check_mypy_ratchet without executing main()."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_mypy_ratchet", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# T1: Baseline YAML schema validation — valid
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _YAML_AVAILABLE, reason="PyYAML not installed")
def test_schema_validation_valid() -> None:
    """A baseline YAML with correct fields passes schema validation."""
    mod = _import_module()
    data = {
        "schema_version": "1",
        "updated_at": "2026-03-09",
        "repos": {
            "assetutilities": {"error_count": 941, "updated_at": "2026-03-09"},
        },
    }
    error = mod._validate_baseline(data)
    assert error is None, f"Expected no error, got: {error}"


# ---------------------------------------------------------------------------
# T2: Baseline YAML schema validation — invalid (missing fields)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _YAML_AVAILABLE, reason="PyYAML not installed")
def test_schema_validation_invalid_missing_repos() -> None:
    """A baseline missing 'repos' key fails schema validation."""
    mod = _import_module()
    data = {"schema_version": "1", "updated_at": "2026-03-09"}
    error = mod._validate_baseline(data)
    assert error is not None
    assert "repos" in error.lower()


@pytest.mark.skipif(not _YAML_AVAILABLE, reason="PyYAML not installed")
def test_schema_validation_invalid_missing_error_count() -> None:
    """A repo entry missing 'error_count' fails schema validation."""
    mod = _import_module()
    data = {
        "repos": {
            "assetutilities": {"updated_at": "2026-03-09"},  # missing error_count
        },
    }
    error = mod._validate_baseline(data)
    assert error is not None
    assert "error_count" in error.lower()


# ---------------------------------------------------------------------------
# T3: Parse "Found N errors in M files" → N
# ---------------------------------------------------------------------------


def test_parse_found_n_errors_output() -> None:
    """Parse standard mypy error summary: 'Found 941 errors in 83 files' → 941."""
    mod = _import_module()
    output = (
        "some/module.py:10: error: Function is missing a return type annotation\n"
        "some/module.py:20: error: Incompatible types\n"
        "Found 941 errors in 83 files (checked 122 source files)\n"
    )
    count = mod._parse_error_count(output)
    assert count == 941, f"Expected 941, got {count}"


# ---------------------------------------------------------------------------
# T4: Parse "Found 1 error in 1 file" → 1
# ---------------------------------------------------------------------------


def test_parse_found_1_error() -> None:
    """Parse singular mypy error summary: 'Found 1 error in 1 file' → 1."""
    mod = _import_module()
    output = (
        "some/module.py:5: error: Invalid syntax  [syntax]\n"
        "Found 1 error in 1 file (errors prevented further checking)\n"
    )
    count = mod._parse_error_count(output)
    assert count == 1, f"Expected 1, got {count}"


# ---------------------------------------------------------------------------
# T5: Parse "Success: no issues found" → 0
# ---------------------------------------------------------------------------


def test_parse_success_no_issues() -> None:
    """Parse mypy success output: 'Success: no issues found' → 0."""
    mod = _import_module()
    output = "Success: no issues found in 5 source files\n"
    count = mod._parse_error_count(output)
    assert count == 0, f"Expected 0, got {count}"


# ---------------------------------------------------------------------------
# T6: Ratchet FAIL (count increased)
# ---------------------------------------------------------------------------


def test_ratchet_fail_count_increased() -> None:
    """check_repo returns FAIL when actual error count exceeds baseline."""
    mod = _import_module()
    result = mod.check_repo("assetutilities", baseline_count=941, actual_count=950)
    assert result["status"] == "fail"
    assert result["actual"] == 950
    assert result["baseline"] == 941


# ---------------------------------------------------------------------------
# T7: Ratchet PASS (count equal)
# ---------------------------------------------------------------------------


def test_ratchet_pass_count_equal() -> None:
    """check_repo returns PASS when actual error count equals baseline."""
    mod = _import_module()
    result = mod.check_repo("assetutilities", baseline_count=941, actual_count=941)
    assert result["status"] == "pass"


# ---------------------------------------------------------------------------
# T8: Ratchet PASS + auto-update baseline (count decreased)
# ---------------------------------------------------------------------------


def test_ratchet_pass_count_decreased() -> None:
    """check_repo returns PASS with improved=True when actual count is below baseline."""
    mod = _import_module()
    result = mod.check_repo("assetutilities", baseline_count=941, actual_count=900)
    assert result["status"] == "pass"
    assert result.get("improved") is True
    assert result["actual"] == 900


# ---------------------------------------------------------------------------
# T9: Missing baseline file → clear error
# ---------------------------------------------------------------------------


def test_missing_baseline_file_exits_with_error(tmp_path: Path) -> None:
    """Script exits non-zero with a clear error message when baseline file is missing."""
    nonexistent = tmp_path / "nonexistent-mypy-baseline.yaml"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--baseline", str(nonexistent)],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    stderr_lower = result.stderr.lower()
    assert "not found" in stderr_lower or "does not exist" in stderr_lower or \
           "no such file" in stderr_lower or "missing" in stderr_lower, \
        f"Expected clear error message, got stderr: {result.stderr!r}"


# ---------------------------------------------------------------------------
# T10: SKIP_MYPY_REASON env var bypass
# ---------------------------------------------------------------------------


def test_skip_mypy_reason_bypass(tmp_path: Path) -> None:
    """When SKIP_MYPY_REASON is set, script exits 0 and prints bypass message."""
    # Create a minimal valid baseline
    baseline = tmp_path / "mypy-baseline.yaml"
    baseline.write_text(
        "schema_version: '1'\nupdated_at: '2026-03-09'\nrepos:\n"
        "  assetutilities:\n    error_count: 941\n    updated_at: '2026-03-09'\n",
        encoding="utf-8",
    )
    env = {**os.environ, "SKIP_MYPY_REASON": "CI environment, skipping mypy checks"}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--baseline", str(baseline)],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"Expected exit 0, got {result.returncode}. stderr={result.stderr}"
    combined = result.stdout + result.stderr
    assert "bypass" in combined.lower() or "skip" in combined.lower(), \
        f"Expected bypass message, got: {combined!r}"


# ---------------------------------------------------------------------------
# T11: --init mode writes baseline with correct counts (unit-level mock)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not _YAML_AVAILABLE, reason="PyYAML not installed")
def test_init_mode_writes_baseline(tmp_path: Path) -> None:
    """--init mode calls main() with mocked _run_mypy and writes a valid baseline YAML."""
    baseline_out = tmp_path / "mypy-baseline.yaml"

    # Build stub repo dirs so the directory-existence check passes
    repo_map = {
        "assetutilities": "assetutilities",
        "digitalmodel": "digitalmodel",
        "worldenergydata": "worldenergydata",
        "assethold": "assethold",
        "ogmanufacturing": "OGManufacturing",
    }
    for repo_name, rel_path in repo_map.items():
        (tmp_path / rel_path / "src").mkdir(parents=True)

    fake_outputs = {
        "assetutilities": "Found 941 errors in 83 files (checked 122 source files)\n",
        "digitalmodel": "Found 1 error in 1 file (errors prevented further checking)\n",
        "worldenergydata": "Found 3414 errors in 547 files (checked 948 source files)\n",
        "assethold": "Found 320 errors in 48 files (checked 85 source files)\n",
        "ogmanufacturing": "Success: no issues found in 5 source files\n",
    }

    def fake_run(cmd, **kwargs):
        cmd_str = " ".join(str(c) for c in cmd)
        # Handle version check — always succeed
        if "--version" in cmd_str:
            mock_result = MagicMock()
            mock_result.stdout = "mypy 1.18.0 (compiled: yes)"
            mock_result.stderr = ""
            mock_result.returncode = 0
            return mock_result
        cwd = kwargs.get("cwd", "")
        cwd_str = str(cwd).lower()
        for repo_name, output in fake_outputs.items():
            if repo_name.lower().replace("_", "") in cwd_str.lower().replace("_", ""):
                mock_result = MagicMock()
                mock_result.stdout = output
                mock_result.stderr = ""
                mock_result.returncode = 0 if "Success" in output else 1
                return mock_result
        mock_result = MagicMock()
        mock_result.stdout = "Success: no issues found in 1 source file\n"
        mock_result.stderr = ""
        mock_result.returncode = 0
        return mock_result

    mod = _import_module()
    # Patch subprocess.run within the loaded module
    with patch.object(mod.subprocess, "run", side_effect=fake_run):
        # Temporarily replace REPOS with our stub mapping
        original_repos = mod.REPOS
        mod.REPOS = repo_map
        try:
            exit_code = mod.main([
                "--init",
                "--baseline", str(baseline_out),
                "--repo-root", str(tmp_path),
            ])
        finally:
            mod.REPOS = original_repos

    assert exit_code == 0, f"--init should return 0, got {exit_code}"
    assert baseline_out.exists(), "--init must write the baseline file"

    data = yaml.safe_load(baseline_out.read_text(encoding="utf-8"))
    assert "repos" in data, "Baseline must have 'repos' key"
    assert "schema_version" in data, "Baseline must have 'schema_version'"
    for repo_entry in data["repos"].values():
        assert "error_count" in repo_entry, "Each repo entry must have 'error_count'"
        assert "updated_at" in repo_entry, "Each repo entry must have 'updated_at'"
    # Validate error counts were correctly parsed
    assert data["repos"]["assetutilities"]["error_count"] == 941
    assert data["repos"]["ogmanufacturing"]["error_count"] == 0


# ---------------------------------------------------------------------------
# T12: check_repos aggregates pass/fail across multiple repos
# ---------------------------------------------------------------------------


def test_check_repos_aggregation() -> None:
    """check_repos returns correct pass/fail lists for multiple repos."""
    mod = _import_module()
    baseline_repos = {
        "assetutilities": {"error_count": 941},
        "digitalmodel": {"error_count": 1},
        "assethold": {"error_count": 320},
    }
    actual_counts = {
        "assetutilities": 941,   # equal → PASS
        "digitalmodel": 0,       # improved → PASS
        "assethold": 350,        # regression → FAIL
    }
    passes, failures = mod.check_repos(baseline_repos, actual_counts)
    pass_repos = {p["repo"] for p in passes}
    fail_repos = {f["repo"] for f in failures}
    assert "assetutilities" in pass_repos
    assert "digitalmodel" in pass_repos
    assert "assethold" in fail_repos


# ---------------------------------------------------------------------------
# T13: Exempt repos are skipped with a note
# ---------------------------------------------------------------------------


def test_exempt_repo_is_skipped() -> None:
    """check_repos skips repos marked exempt=true (requires exempt_reason)."""
    mod = _import_module()
    baseline_repos = {
        "worldenergydata": {
            "error_count": 3414,
            "exempt": True,
            "exempt_reason": "Too many pre-existing errors; tracked separately",
        },
    }
    actual_counts = {"worldenergydata": 9999}  # would fail if not exempt
    passes, failures = mod.check_repos(baseline_repos, actual_counts)
    assert len(failures) == 0, "Exempt repo should not appear in failures"
    assert any(p["status"] == "exempt" for p in passes), "Exempt repo should appear in passes"
