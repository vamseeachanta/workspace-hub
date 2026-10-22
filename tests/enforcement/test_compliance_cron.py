"""Alert regressions derived from issue 3808 and independent count arithmetic."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def report(reviewed=0, unreviewed=0, skipped=7):
    """Synthetic counts: rate = floor(100 * reviewed / reviewable), if nonzero."""
    reviewable = reviewed + unreviewed
    rate = reviewed * 100 // reviewable if reviewable else 0
    # Source: issue 3808, Thresholds table (2026): default pass boundary = 80%.
    return {"total_commits": reviewable + skipped, "skipped": skipped,
            "reviewable": reviewable, "reviewed": reviewed, "unreviewed": unreviewed,
            "compliance_rate": rate, "threshold": 80,
            "verdict": "FAIL" if reviewable and rate < 80 else "PASS",
            "stage_prompt_drift": {"verdict": "pass"}}


def run_cron(tmp_path, payload, *, raw=None, status=None):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("compliance-cron.sh", "compliance_report.py"):
        source = ROOT / "scripts/enforcement" / name
        if source.exists():
            shutil.copy(source, scripts / name)
    output = "JSON Report:\n" + json.dumps(payload) if raw is None else raw
    (tmp_path / "output").write_text(output)
    code = status if status is not None else int(payload.get("verdict") == "FAIL")
    dashboard = scripts / "compliance-dashboard.sh"
    dashboard.write_text(f'#!/bin/bash\ncat "$FIXTURE_ROOT/output"\nexit {code}\n')
    dashboard.chmod(0o755)
    tools = tmp_path / "bin"
    tools.mkdir()
    for name, body in {
        "git": 'echo "$FIXTURE_ROOT"',
        "gh": 'echo "$*" >> "$FIXTURE_ROOT/gh-calls"; exit 0',
    }.items():
        path = tools / name
        path.write_text("#!/bin/bash\n" + body + "\n")
        path.chmod(0o755)
    env = {key: value for key, value in os.environ.items()
           if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}}
    env.update(FIXTURE_ROOT=str(tmp_path), DRY_RUN="true",
               PATH=str(tools) + os.pathsep + env["PATH"])
    result = subprocess.run(["bash", str(scripts / "compliance-cron.sh")],
                            env=env, capture_output=True, text=True, check=False)
    log = next((tmp_path / "logs/compliance").glob("daily-*.log")).read_text()
    return result, log


@pytest.mark.parametrize("skipped", [0, 7])
def test_no_reviewable_commits_do_not_alert(tmp_path, skipped):
    """Issue 3808: 7 - 7 = 0 reviewable; 0/0 is not a failed review rate."""
    result, log = run_cron(tmp_path, report(skipped=skipped))
    assert result.returncode == 0
    assert "No reviewable commits" in log
    assert "ALERT:" not in log
    assert not (tmp_path / "gh-calls").exists()


@pytest.mark.parametrize(("reviewed", "unreviewed", "severity"), [
    (0, 7, "critical"), (3, 7, "high"), (5, 5, "medium"),
    (8, 2, None), (10, 0, None),
    (29, 71, "critical"), (49, 51, "high"), (79, 21, "medium"),
])
def test_thresholds_and_top_level_verdict(tmp_path, reviewed, unreviewed, severity):
    """Hand calculation: 0/7, 3/10, 5/10, 8/10, 10/10 times 100.

    Additional boundary cases use 29/100, 49/100 and 79/100 times 100.
    Boundaries are the Thresholds table in issue 3808 (2026).
    """
    result, log = run_cron(tmp_path, report(reviewed, unreviewed, skipped=0))
    assert result.returncode == 0
    if severity:
        assert f"severity: {severity}" in log
        assert "**Dashboard verdict:** FAIL\n" in log
        assert "**Reviewable:**" in log
    else:
        assert "ALERT:" not in log
    assert not (tmp_path / "gh-calls").exists(), "Dry run must not contact GitHub"


@pytest.mark.parametrize("mutation", [
    {"reviewable": 1}, {"compliance_rate": 100}, {"verdict": "PASS"},
    {"reviewed": -1}, {"reviewed": True}, {"unreviewed": "7"},
    {"threshold": 101},
])
def test_inconsistent_reports_fail_without_alert(tmp_path, mutation):
    payload = report(0, 7, 0)
    payload.update(mutation)
    result, log = run_cron(tmp_path, payload)
    assert result.returncode != 0
    assert "ERROR:" in log
    assert "ALERT:" not in log
    assert not (tmp_path / "gh-calls").exists()


@pytest.mark.parametrize("raw", ["No commits in window", 'JSON Report:\n{"verdict":', 'JSON Report:\n[]', 'JSON Report:\nnull'])
def test_missing_or_invalid_json_is_an_error(tmp_path, raw):
    result, log = run_cron(tmp_path, {}, raw=raw)
    assert result.returncode != 0
    assert "ERROR:" in log


def test_dashboard_execution_error_is_not_a_compliance_alert(tmp_path):
    result, log = run_cron(tmp_path, report(0, 7, 0), status=2)
    assert result.returncode != 0
    assert "ERROR:" in log
    assert "ALERT:" not in log


def test_dashboard_threshold_is_used(tmp_path):
    """Hand calculation: 9/10 * 100 = 90; required input threshold 95 fails."""
    payload = report(9, 1, 0)
    payload.update(threshold=95, verdict="FAIL")
    result, log = run_cron(tmp_path, payload)
    assert result.returncode == 0
    assert "severity: medium" in log
    assert ">= 95%" in log


def test_pretty_json_with_dashboard_trailer(tmp_path):
    """Producer emits formatted JSON followed by the saved-report message."""
    payload = report(0, 7, 0)
    output = "JSON Report:\n" + json.dumps(payload, indent=2)
    output += "\n\nReport saved to: report.json\n"
    result, log = run_cron(tmp_path, payload, raw=output)
    assert result.returncode == 0
    assert "**Dashboard verdict:** FAIL\n" in log
