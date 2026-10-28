"""CLI contract from issue #4227, independent of the decision implementation.

Hand calculation: four results per job, two scopes, two matrix sizes and two
modes give 4 * 4 * 2 * 2 * 2 = 128 invocations. Exit codes zero/one and matrix
sizes zero/one are the contract's pass/fail and empty/nonempty examples.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Repository layout: this file's parents are ci, tests, then the checkout root.
ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/ci/domain_matrix_aggregate.py"

# Independent literal conjunction: only success/success passes (issue #4227).
JOB_RESULTS = {
    "success": {"success": 0, "failure": 1, "cancelled": 1, "skipped": 1},
    "failure": {"success": 1, "failure": 1, "cancelled": 1, "skipped": 1},
    "cancelled": {"success": 1, "failure": 1, "cancelled": 1, "skipped": 1},
    "skipped": {"success": 1, "failure": 1, "cancelled": 1, "skipped": 1},
}
CASES = [
    (discover, test_domain, job_code, scope, size, advisory)
    for discover, row in JOB_RESULTS.items()
    for test_domain, job_code in row.items()
    for scope in ("modules", "skip")
    for size in (0, 1)
    for advisory in (False, True)
]


@pytest.fixture(scope="module", params=CASES)
def cli_case(request, tmp_path_factory):
    """Share each real invocation between predicate and diagnostic assertions."""
    discover, test_domain, _, scope, size, advisory = request.param
    cwd = tmp_path_factory.mktemp("aggregate-cli")
    assert not cwd.resolve().is_relative_to(ROOT)
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    command = [sys.executable, str(SCRIPT), discover, test_domain, scope, str(size)]
    if advisory:
        command.append("--advisory")
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        shell=False,
        check=False,
    )
    return request.param, result


def test_cli_truth_table_matches_independent_predicates(cli_case):
    inputs, result = cli_case
    discover, test_domain, job_code, scope, size, advisory = inputs
    # Hand predicate: advisory uses the conjunction; strict also needs size one.
    expected = job_code if advisory or size == 1 else 1
    assert result.returncode == expected
    reported = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition(":")
        if separator and key in ("discover", "test-domain", "scope", "matrix size"):
            assert key not in reported
            reported[key] = value.strip()
    assert reported == {
        "discover": discover,
        "test-domain": test_domain,
        "scope": scope,
        "matrix size": str(size),
    }
    assert "Traceback" not in result.stdout + result.stderr
    assert not result.stderr


def test_cli_annotations_match_strict_and_advisory_modes(cli_case):
    inputs, result = cli_case
    _, _, job_code, _, size, advisory = inputs
    # Empty matrices still warn when advisory mode returns a successful exit.
    rejected_strict_predicate = job_code == 1 or size == 0
    expected = job_code if advisory or size == 1 else 1
    assert result.returncode == expected
    if rejected_strict_predicate:
        annotation = "::warning::" if advisory else "::error::"
        assert annotation in result.stdout
        other_annotation = "::error::" if advisory else "::warning::"
        assert other_annotation not in result.stdout + result.stderr
    assert "Traceback" not in result.stdout + result.stderr
