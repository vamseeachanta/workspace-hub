"""Independent conjunction table from the existing workflow and issue #4227.

Hand calculation: a conjunction is true only for (success, success).
For each scope, a positive matrix uses that table; an empty matrix always fails.
Scope is diagnostic, including skip and empty: it never excuses failed jobs.
"""

import runpy
import subprocess
import sys
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2] / "scripts/ci/domain_matrix_aggregate.py"
# Rows: discover; columns: test-domain. Written by hand, not from the decision.
TABLE = {
    "success": {"success": 0, "failure": 1, "cancelled": 1, "skipped": 1},
    "failure": {"success": 1, "failure": 1, "cancelled": 1, "skipped": 1},
    "cancelled": {"success": 1, "failure": 1, "cancelled": 1, "skipped": 1},
    "skipped": {"success": 1, "failure": 1, "cancelled": 1, "skipped": 1},
}


@pytest.fixture
def script(tmp_path):
    target = tmp_path / SOURCE.name
    target.write_bytes(SOURCE.read_bytes())
    return target


@pytest.mark.parametrize("scope", ["full", "modules", "skip", ""])
@pytest.mark.parametrize("discover,test,expected", [
    (d, t, result) for d, row in TABLE.items() for t, result in row.items()
])
@pytest.mark.parametrize("size", [0, 1])
def test_truth_table(script, scope, discover, test, expected, size):
    decide = runpy.run_path(str(script))["decide"]
    rc, message = decide(discover, test, scope, size)
    assert rc == (expected if size else 1)
    assert message


@pytest.mark.parametrize("size", ["0", "-1", "invalid"])
def test_cli_fails_closed(script, size):
    result = subprocess.run(
        [sys.executable, str(script), "success", "success", "full", size],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode != 0


def test_advisory_preserves_legacy_empty_matrix_result(script):
    result = subprocess.run(
        [sys.executable, str(script), "success", "success", "skip", "0", "--advisory"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0
    assert "::warning::" in result.stdout


def test_advisory_does_not_hide_failed_jobs(script):
    result = subprocess.run(
        [sys.executable, str(script), "success", "skipped", "skip", "0", "--advisory"],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 1
