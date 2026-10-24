"""Alert regressions for issue 3813; all counts are synthetic hand calculations."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts/enforcement"
PARSER = SCRIPTS / "compliance-alert-report.py"


def report(reviewed=0, unreviewed=0, skipped=7):
    """Guide: floor(100 * reviewed / (reviewed + unreviewed)); zero means no rate."""
    reviewable = reviewed + unreviewed
    rate = reviewed * 100 // reviewable if reviewable else 0
    return {
        "total_commits": reviewable + skipped,
        "skipped": skipped,
        "reviewable": reviewable,
        "reviewed": reviewed,
        "unreviewed": unreviewed,
        "compliance_rate": rate,
        "threshold": 80,  # Issue 3813, Thresholds table (2026-08-24).
        "verdict": "FAIL" if reviewable and rate < 80 else "PASS",
        "stage_prompt_drift": {"latest_event": {"verdict": "pass"}},
    }


def output(payload):
    return "Compliance rate:    0%\nJSON Report:\n" + json.dumps(payload) + "\n\nReport saved to: report.json\n"


def parse(text, status=0):
    return subprocess.run(
        ["python3", str(PARSER), "--dashboard-status", str(status)],
        input=text, text=True, capture_output=True, check=False,
    )


@pytest.mark.parametrize("skipped", [0, 7])
def test_zero_denominator_is_not_a_compliance_failure(skipped):
    """0 reviewed / 0 reviewable is undefined, even with seven skipped commits."""
    result = parse(output(report(skipped=skipped)))
    assert result.returncode == 0
    assert result.stdout.strip() == f"NO_REVIEWABLE\t0\t{skipped}\t0\t0\tPASS"


def test_nested_verdict_and_human_rate_are_not_alert_inputs():
    """1 reviewed / 2 reviewable * 100 = 50%, despite the human text's 0%."""
    result = parse(output(report(1, 1)), status=1)
    assert result.returncode == 0
    assert result.stdout.strip() == "EVALUATED\t50\t9\t1\t1\tFAIL"


@pytest.mark.parametrize("mutation", [
    {"reviewable": 1}, {"total_commits": 8}, {"reviewed": -1},
    {"reviewed": True}, {"compliance_rate": 1}, {"verdict": "FAIL"},
    {"threshold": 101}, {"unreviewed": "0"},
])
def test_invalid_or_inconsistent_metrics_are_errors(mutation):
    payload = report()
    payload.update(mutation)
    result = parse(output(payload))
    assert result.returncode != 0
    assert result.stdout == ""
    assert "Invalid compliance report:" in result.stderr


@pytest.mark.parametrize("text", ["", "Compliance rate: 0%", "JSON Report:\n{", "JSON Report:\n[]", "JSON Report:\n{}"])
def test_missing_or_malformed_report_is_not_a_pass(text):
    result = parse(text)
    assert result.returncode != 0
    assert "Invalid compliance report:" in result.stderr


@pytest.mark.parametrize("status", [1, 2, 127])
def test_execution_failure_cannot_be_hidden_by_pass_payload(status):
    result = parse(output(report()), status=status)
    assert result.returncode != 0
    assert "Invalid compliance report:" in result.stderr


def test_fail_payload_requires_dashboard_failure_status():
    result = parse(output(report(0, 1)), status=0)
    assert result.returncode != 0
    assert "Invalid compliance report:" in result.stderr


def run_cron(tmp_path, payload, status=0, raw=None, real_dashboard=False, dry_run=True):
    repo = tmp_path / "repo"
    script_dir = repo / "scripts/enforcement"
    script_dir.mkdir(parents=True)
    env = os.environ.copy()
    # Fixture Git bindings must never redirect initialization to the caller.
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE"):
        env.pop(key, None)
    subprocess.run(["git", "init", str(repo)], env=env, check=True, capture_output=True)
    for name in ("compliance-cron.sh", "compliance-alert-report.py"):
        shutil.copyfile(SCRIPTS / name, script_dir / name)
    dashboard = script_dir / "compliance-dashboard.sh"
    text = raw if raw is not None else output(payload)
    dashboard.write_text(f"#!/bin/bash\ncat <<'REPORT'\n{text}\nREPORT\nexit {status}\n")
    if real_dashboard:
        shutil.copyfile(SCRIPTS / "compliance-dashboard.sh", dashboard)
    dashboard.chmod(0o755)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text('#!/bin/bash\necho called >> "$GH_CALLS"\nexit 99\n')
    gh.chmod(0o755)
    calls = tmp_path / "gh-calls"
    env.update(PATH=f"{bin_dir}:{env['PATH']}", DRY_RUN="true" if dry_run else "false", GH_CALLS=str(calls))
    result = subprocess.run(["bash", str(script_dir / "compliance-cron.sh")],
                            cwd=repo, env=env, text=True, capture_output=True, check=False)
    logs = list((repo / "logs/compliance").glob("daily-*.log"))
    assert len(logs) == 1
    assert not calls.exists(), "Dry runs and invalid reports must not contact GitHub"
    return result, logs[0].read_text()


@pytest.mark.parametrize("skipped", [0, 7])
def test_cron_does_not_alert_on_empty_denominator(tmp_path, skipped):
    result, log = run_cron(tmp_path, report(skipped=skipped))
    assert result.returncode == 0
    assert "No reviewable commits" in log
    assert "ALERT:" not in log


@pytest.mark.parametrize(("reviewed", "severity"), [
    (0, "critical"), (29, "critical"), (30, "high"), (49, "high"),
    (50, "medium"), (79, "medium"), (80, None), (100, None),
])
def test_cron_threshold_boundaries(tmp_path, reviewed, severity):
    """Of 100 reviewable commits, R reviewed gives R%; issue 3813 threshold table."""
    payload = report(reviewed, 100 - reviewed)
    result, log = run_cron(tmp_path, payload, status=1 if reviewed < 80 else 0)
    assert result.returncode == 0
    if severity:
        assert f"severity: {severity}" in log
        assert "[DRY RUN] Would create/update issue:" in log
        assert "**Dashboard verdict:** FAIL\n" in log
        assert "FAIL\npass" not in log
    else:
        assert "PASS: Compliance" in log
        assert "ALERT:" not in log


@pytest.mark.parametrize("dry_run", [True, False])
def test_cron_missing_report_fails_without_alert(tmp_path, dry_run):
    result, log = run_cron(tmp_path, {}, status=2, raw="dashboard failed", dry_run=dry_run)
    assert result.returncode == 1
    assert "ERROR: Invalid compliance report" in log
    assert "ALERT:" not in log


def test_actual_dashboard_empty_repository_is_not_an_alert(tmp_path):
    result, log = run_cron(tmp_path, {}, real_dashboard=True, dry_run=False)
    assert result.returncode == 0
    assert "No reviewable commits" in log
    assert "ALERT:" not in log


def test_duplicate_json_metric_is_rejected():
    text = output(report()).replace('"reviewed": 0', '"reviewed": 0, "reviewed": 0')
    result = parse(text)
    assert result.returncode == 1
    assert "duplicate field: reviewed" in result.stderr


def test_integer_rate_matches_dashboard_truncation():
    """2 reviewed / 3 reviewable: floor(200 / 3) = 66, not rounded 67."""
    result = parse(output(report(2, 1)), status=1)
    assert result.returncode == 0
    assert result.stdout.strip() == "EVALUATED\t66\t10\t2\t1\tFAIL"
