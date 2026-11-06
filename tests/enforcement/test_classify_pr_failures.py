"""Tests for scripts/ci_health/classify-pr-failures.sh (wh#3368).

Classifies a PR's failing checks as BASELINE (also red on the base branch) vs
REGRESSION / NEW / UNKNOWN. Tests stub `gh` via GH_BIN with a dispatcher that
serves per-call fixtures from a temp dir — no network, no real repo state.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "ci_health" / "classify-pr-failures.sh"

FAKE_GH = r"""#!/usr/bin/env bash
# Dispatch on the call type; emit the matching fixture file (already in the
# shape the real `gh ... -q` would produce). Missing fixture -> empty output.
args="$*"
d="$FAKE_DIR"
emit() { [[ -f "$d/$1" ]] && cat "$d/$1" || true; }
case "$args" in
  *"pr checks"*)             emit pr_checks ;;
  *"check-runs"*)            emit check_runs ;;
  *"commits/"*"/status"*)    emit status ;;
  *"pr view"*)               emit base ;;
  *"repo view"*)             emit repo ;;
  *)                         exit 0 ;;
esac
"""


def _make_gh(tmp_path: Path, *, pr_checks="", check_runs="", status="", base="main",
             repo="vamseeachanta/digitalmodel") -> tuple[Path, dict]:
    d = tmp_path / "fx"
    d.mkdir()
    (d / "pr_checks").write_text(pr_checks)
    (d / "check_runs").write_text(check_runs)
    (d / "status").write_text(status)
    (d / "base").write_text(base + "\n")
    (d / "repo").write_text(repo + "\n")
    gh = tmp_path / "gh"
    gh.write_text(FAKE_GH)
    gh.chmod(0o755)
    return gh, {"FAKE_DIR": str(d)}


def _run(*args, gh_bin, env_extra):
    env = os.environ.copy()
    env["GH_BIN"] = str(gh_bin)
    env.update(env_extra)
    return subprocess.run(
        ["bash", str(SCRIPT), *args], capture_output=True, text=True, env=env
    )


def test_all_failures_baseline_passes(tmp_path: Path):
    gh, env = _make_gh(
        tmp_path,
        pr_checks="Atlas staleness check\nCI harness and compliance tests\n",
        check_runs=(
            "Atlas staleness check\tcompleted\tfailure\n"
            "CI harness and compliance tests\tcompleted\tfailure\n"
            "tests-subsea\tcompleted\tsuccess\n"
        ),
    )
    r = _run("1343", "--repo", "vamseeachanta/digitalmodel", "--base", "main",
             gh_bin=gh, env_extra=env)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "2 baseline, 0 regression" in r.stdout
    assert "BASELINE" in r.stdout


def test_regression_detected_fails(tmp_path: Path):
    gh, env = _make_gh(
        tmp_path,
        pr_checks="tests-foo\nAtlas staleness check\n",
        check_runs=(
            "tests-foo\tcompleted\tsuccess\n"          # green on main -> regression
            "Atlas staleness check\tcompleted\tfailure\n"
        ),
    )
    r = _run("42", "--repo", "o/r", "--base", "main", gh_bin=gh, env_extra=env)
    assert r.returncode == 1
    assert "REGRESSION" in r.stdout
    assert "1 regression" in r.stdout


def test_new_check_absent_on_base_fails(tmp_path: Path):
    gh, env = _make_gh(
        tmp_path,
        pr_checks="brand-new-check\n",
        check_runs="tests-subsea\tcompleted\tsuccess\n",  # name not present
    )
    r = _run("42", "--repo", "o/r", "--base", "main", gh_bin=gh, env_extra=env)
    assert r.returncode == 1
    assert "NEW" in r.stdout


def test_pending_on_base_is_unknown(tmp_path: Path):
    gh, env = _make_gh(
        tmp_path,
        pr_checks="Run Quality Gates\n",
        check_runs="Run Quality Gates\tin_progress\t\n",  # not concluded
    )
    r = _run("42", "--repo", "o/r", "--base", "main", gh_bin=gh, env_extra=env)
    assert r.returncode == 1
    assert "UNKNOWN" in r.stdout


def test_no_failures_passes(tmp_path: Path):
    gh, env = _make_gh(tmp_path, pr_checks="")
    r = _run("42", "--repo", "o/r", "--base", "main", gh_bin=gh, env_extra=env)
    assert r.returncode == 0
    assert "no failing checks" in r.stdout


def test_legacy_status_context_classifies_baseline(tmp_path: Path):
    # check-runs empty; the failing context only appears in legacy statuses.
    gh, env = _make_gh(
        tmp_path,
        pr_checks="security/scan\n",
        check_runs="",
        status="security/scan\tfailure\n",
    )
    r = _run("42", "--repo", "o/r", "--base", "main", gh_bin=gh, env_extra=env)
    assert r.returncode == 0
    assert "BASELINE" in r.stdout


def test_base_inferred_from_pr_when_not_passed(tmp_path: Path):
    gh, env = _make_gh(
        tmp_path,
        pr_checks="Atlas staleness check\n",
        check_runs="Atlas staleness check\tcompleted\tfailure\n",
        base="develop",
    )
    r = _run("42", "--repo", "o/r", gh_bin=gh, env_extra=env)  # no --base
    assert r.returncode == 0
    assert "base 'develop'" in r.stdout


def test_missing_pr_arg_is_usage_error(tmp_path: Path):
    gh, env = _make_gh(tmp_path)
    r = _run("--repo", "o/r", gh_bin=gh, env_extra=env)
    assert r.returncode == 2


# Expected records are authored from the report protocol in
# scripts/ci_health/classify-pr-failures.sh (Method, Exit codes, conclusion
# tables, and Summary). Each fixture has one failing PR check: the counts below
# are hand-counted, and exit codes follow the documented all-baseline rule.
_SINGLE_CHECK_REPORT = {
    "BASELINE": (0, "Summary: 1 baseline, 0 regression, 0 new, 0 unknown"),
    "REGRESSION": (1, "Summary: 0 baseline, 1 regression, 0 new, 0 unknown"),
    "UNKNOWN": (1, "Summary: 0 baseline, 0 regression, 0 new, 1 unknown"),
    "NEW": (1, "Summary: 0 baseline, 0 regression, 1 new, 0 unknown"),
}


def _assert_protocol_report(result, expected_label):
    expected_exit, expected_summary = _SINGLE_CHECK_REPORT[expected_label]
    assert result.returncode == expected_exit, result.stdout + result.stderr
    header, record, summary, *notes = result.stdout.splitlines()
    assert header == "PR #42 (o/r) failing checks vs base 'main':"
    # Keep the check name's spaces while allowing the report's column padding.
    assert record.strip().split(maxsplit=1) == [expected_label, "protocol check"]
    assert summary == expected_summary
    if expected_label == "BASELINE":
        assert notes == [
            "  → all failures are pre-existing on 'main' (baseline-red); safe "
            "to merge past per the non-required-failing policy."
        ]
        assert result.stderr == ""
    else:
        assert notes == []
        assert result.stderr == (
            "  → not all failures are baseline; investigate the "
            "regression/new/unknown checks before merging.\n"
        )


@pytest.mark.parametrize(
    "status, conclusion, expected_label",
    [
        # Matching red base snapshots: all terminal red outcomes are baseline.
        ("completed", "failure", "BASELINE"),
        ("completed", "timed_out", "BASELINE"),
        ("completed", "cancelled", "BASELINE"),
        ("completed", "action_required", "BASELINE"),
        ("completed", "startup_failure", "BASELINE"),
        ("completed", "stale", "BASELINE"),
        # Contrasting non-failing base snapshots: each is a regression.
        ("completed", "success", "REGRESSION"),
        ("completed", "neutral", "REGRESSION"),
        ("completed", "skipped", "REGRESSION"),
        # Incomplete evidence cannot establish either a red or green base.
        ("queued", "", "UNKNOWN"),
        ("requested", "", "UNKNOWN"),
        ("waiting", "", "UNKNOWN"),
        ("pending", "", "UNKNOWN"),
        ("in_progress", "", "UNKNOWN"),
        ("in_progress", "failure", "UNKNOWN"),
        ("in_progress", "success", "UNKNOWN"),
        ("completed", "", "UNKNOWN"),
        ("completed", "unrecognized", "UNKNOWN"),
        # No matching base observation is distinct from a pending observation.
        (None, None, "NEW"),
    ],
)
def test_check_run_conclusion_protocol(
    tmp_path: Path, status, conclusion, expected_label
):
    check_runs = (
        "unrelated check\tcompleted\tfailure\n"
        if status is None
        else f"protocol check\t{status}\t{conclusion}\n"
    )
    gh, env = _make_gh(
        tmp_path, pr_checks="protocol check\n", check_runs=check_runs
    )
    result = _run(
        "42", "--repo", "o/r", "--base", "main", gh_bin=gh, env_extra=env
    )
    _assert_protocol_report(result, expected_label)


@pytest.mark.parametrize("source", ["check_runs", "status"])
@pytest.mark.parametrize(
    "latest, older, expected_label",
    [
        ("failure", "success", "BASELINE"),
        ("success", "failure", "REGRESSION"),
        ("pending", "failure", "UNKNOWN"),
        ("pending", "success", "UNKNOWN"),
        ("failure", "pending", "BASELINE"),
        ("success", "pending", "REGRESSION"),
    ],
)
def test_latest_same_name_observation_wins(
    tmp_path: Path, source, latest, older, expected_label
):
    # The report protocol consumes newest-first snapshots. Put conflicting
    # older evidence last, including cases where the latest is still pending.
    records = []
    for state in (latest, older):
        if source == "check_runs":
            observation = (
                "in_progress\t" if state == "pending" else f"completed\t{state}"
            )
        else:
            observation = state
        records.append(f"protocol check\t{observation}\n")
    gh, env = _make_gh(
        tmp_path, pr_checks="protocol check\n", **{source: "".join(records)}
    )
    result = _run(
        "42", "--repo", "o/r", "--base", "main", gh_bin=gh, env_extra=env
    )
    _assert_protocol_report(result, expected_label)


@pytest.mark.parametrize(
    "check_run, legacy_state, expected_label",
    [
        ("completed\tfailure", "success", "BASELINE"),
        ("completed\tfailure", "pending", "BASELINE"),
        ("completed\tsuccess", "failure", "REGRESSION"),
        ("completed\tsuccess", "error", "REGRESSION"),
        ("completed\tsuccess", "pending", "REGRESSION"),
        ("in_progress\t", "failure", "UNKNOWN"),
        ("in_progress\t", "error", "UNKNOWN"),
        ("in_progress\t", "success", "UNKNOWN"),
        ("completed\t", "failure", "UNKNOWN"),
        ("completed\tunrecognized", "success", "UNKNOWN"),
    ],
)
def test_check_run_takes_precedence_over_legacy_status(
    tmp_path: Path, check_run, legacy_state, expected_label
):
    # Legacy statuses only fill gaps; even pending check-runs own their names.
    # The unrelated context also proves that name matching is exact.
    gh, env = _make_gh(
        tmp_path,
        pr_checks="protocol check\n",
        check_runs=f"protocol check\t{check_run}\n",
        status=(
            "unrelated check\tfailure\n"
            f"protocol check\t{legacy_state}\n"
        ),
    )
    result = _run(
        "42", "--repo", "o/r", "--base", "main", gh_bin=gh, env_extra=env
    )
    _assert_protocol_report(result, expected_label)
