"""Cron regression cases use independent integer arithmetic.

Policy source: issue 3814, Thresholds (2026-08-31), and the dashboard's
Calculate rates section: floor(100 * reviewed / reviewable).
Fixtures are synthetic counts, not historical review evidence.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/enforcement/compliance-cron.sh"


def report(reviewed=0, unreviewed=0, skipped=7):
    """Hand calculation: reviewable = reviewed + unreviewed; total adds skipped."""
    reviewable = reviewed + unreviewed
    return {
        "total_commits": reviewable + skipped,
        "skipped": skipped,
        "reviewable": reviewable,
        "reviewed": reviewed,
        "unreviewed": unreviewed,
        "compliance_rate": reviewed * 100 // reviewable if reviewable else 0,
        "verdict": "FAIL" if unreviewed else "PASS",
        "stage_prompt_drift": {"latest_event": {"verdict": "pass"}},
    }


def invoke(tmp_path, payload, *, status=0, raw=None, dry_run=True):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    shutil.copyfile(SCRIPT, scripts / SCRIPT.name)
    output = tmp_path / "dashboard.txt"
    output.write_text(raw if raw is not None else (
        "Compliance rate:    0% (threshold: 80%)\nJSON Report:\n"
        + json.dumps(payload) + "\n\nReport saved to: report.json\n"
    ))
    dashboard = scripts / "compliance-dashboard.sh"
    dashboard.write_text(f'#!/bin/bash\ncat "$FIXTURE_OUTPUT"\nexit {status}\n')
    dashboard.chmod(0o755)
    binaries = tmp_path / "bin"
    binaries.mkdir()
    for name, body in {
        "git": 'echo "$FIXTURE_ROOT"',
        "gh": 'echo unexpected-gh-call >> "$GH_CALLS"; exit 99',
    }.items():
        executable = binaries / name
        executable.write_text("#!/bin/bash\n" + body + "\n")
        executable.chmod(0o755)
    env = {key: value for key, value in os.environ.items()
           if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}}
    env.update(PATH=str(binaries) + os.pathsep + env["PATH"],
               FIXTURE_ROOT=str(tmp_path), FIXTURE_OUTPUT=str(output),
               GH_CALLS=str(tmp_path / "gh-calls"), DRY_RUN=str(dry_run).lower())
    result = subprocess.run(["bash", str(scripts / SCRIPT.name)], cwd=tmp_path,
                            env=env, capture_output=True, text=True, check=False)
    log = next((tmp_path / "logs/compliance").glob("daily-*.log")).read_text()
    assert not (tmp_path / "gh-calls").exists()
    return result, log


@pytest.mark.parametrize("skipped", [0, 7])
@pytest.mark.parametrize("dry_run", [True, False])
def test_empty_denominator_does_not_alert(tmp_path, skipped, dry_run):
    """Zero reviewable commits has no fraction; seven skipped reproduces the alert."""
    result, log = invoke(tmp_path, report(skipped=skipped), dry_run=dry_run)
    assert result.returncode == 0
    assert "No reviewable commits" in log
    assert "ALERT:" not in log


@pytest.mark.parametrize("reviewed,unreviewed,rate,severity", [
    (0, 5, 0, "critical"), (1, 3, 25, "critical"), (29, 71, 29, "critical"),
    (3, 7, 30, "high"), (49, 51, 49, "high"), (1, 1, 50, "medium"),
    (3, 2, 60, "medium"), (79, 21, 79, "medium"),
    (4, 1, 80, None), (5, 0, 100, None),
])
def test_thresholds_and_top_level_fields(tmp_path, reviewed, unreviewed, rate, severity):
    """Hand results: 0/5, 1/4, 3/10, 1/2, 3/5, 4/5, 5/5 times 100.

    Additional boundary results: 29/100, 49/100 and 79/100 times 100.
    Boundaries and severity are from issue 3814, Thresholds (2026-08-31).
    """
    payload = report(reviewed, unreviewed)
    payload["verdict"] = "FAIL" if rate < 80 else "PASS"
    result, log = invoke(tmp_path, payload, status=int(rate < 80))
    assert result.returncode == 0
    assert f"Compliance rate: {rate}%" in log
    if severity:
        assert f"severity: {severity}" in log
        assert f"**Reviewed:** {reviewed} | **Unreviewed:** {unreviewed}" in log
        assert "**Dashboard verdict:** FAIL\n" in log
        assert "[DRY RUN] Would create/update issue" in log
    else:
        assert "ALERT:" not in log


@pytest.mark.parametrize("field,value", [
    ("reviewable", 2), ("reviewed", -1), ("total_commits", 0),
    ("compliance_rate", "0"), ("compliance_rate", False), ("compliance_rate", 101),
    ("unreviewed", None), ("skipped", 0.5), ("verdict", "unknown"),
])
def test_invalid_reports_fail_without_alert(tmp_path, field, value):
    payload = report()
    payload[field] = value
    result, log = invoke(tmp_path, payload)
    assert result.returncode == 1
    assert "Invalid dashboard report" in log
    assert "ALERT:" not in log


@pytest.mark.parametrize("raw", ["", "not JSON", 'JSON Report:\n{"reviewed": 0}'])
def test_missing_or_partial_report_is_an_error(tmp_path, raw):
    result, log = invoke(tmp_path, None, raw=raw)
    assert result.returncode == 1
    assert "Invalid dashboard report" in log
    assert "ALERT:" not in log


def test_dashboard_execution_error_is_not_a_compliance_alert(tmp_path):
    result, log = invoke(tmp_path, report(), status=2)
    assert result.returncode == 1
    assert "Dashboard execution failed" in log
    assert "ALERT:" not in log


def test_json_formatting_does_not_change_counts(tmp_path):
    payload = report(3, 2)
    result, log = invoke(tmp_path, payload, status=1,
                         raw="JSON Report:\n" + json.dumps(payload, indent=2))
    assert result.returncode == 0
    assert "Compliance rate: 60%" in log
    assert "**Dashboard verdict:** FAIL\n" in log


def test_integer_percentage_truncates(tmp_path):
    """Independent hand calculation: 100 * 2 / 3 = 66 + 2/3; floor is 66."""
    result, log = invoke(tmp_path, report(2, 1), status=1)
    assert result.returncode == 0
    assert "Compliance rate: 66%" in log


def test_actual_dashboard_empty_window(tmp_path):
    """No git history gives zero total and reviewable; no alert is warranted."""
    # Run the actual producer outside any Git checkout, then consume its output.
    original = SCRIPT.parent / "compliance-dashboard.sh"
    raw = subprocess.run(
        ["bash", str(original)], cwd=tmp_path,
        env={key: value for key, value in os.environ.items()
             if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}},
        capture_output=True, text=True, check=False,
    )
    assert raw.returncode == 0
    result, log = invoke(tmp_path, None, raw=raw.stdout)
    assert result.returncode == 0
    assert "No reviewable commits" in log


@pytest.mark.parametrize("status,payload", [(1, report()), (0, report(0, 5))])
def test_exit_status_must_match_report(tmp_path, status, payload):
    result, log = invoke(tmp_path, payload, status=status)
    assert result.returncode == 1
    assert "Invalid dashboard report" in log
    assert "ALERT:" not in log
