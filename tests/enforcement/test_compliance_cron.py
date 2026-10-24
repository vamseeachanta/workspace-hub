"""Isolated alert regressions; expected arithmetic is stated independently."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2] / "scripts/enforcement/compliance-cron.sh"


def run_cron(tmp_path, report, dashboard_status=0, raw=None):
    """Run copied scripts with fake GitHub and Git commands; no repository writes."""
    scripts = tmp_path / "scripts/enforcement"
    scripts.mkdir(parents=True)
    shutil.copy2(SOURCE, scripts / SOURCE.name)
    shutil.copy2(SOURCE.with_name("compliance-summary.py"), scripts)
    payload = raw if raw is not None else "JSON Report:\n" + json.dumps(report)
    dashboard = scripts / "compliance-dashboard.sh"
    dashboard.write_text(
        "#!/bin/bash\ncat <<'REPORT'\n"
        + payload
        + f"\nREPORT\nexit {dashboard_status}\n"
    )
    dashboard.chmod(0o755)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    calls = tmp_path / "github-calls"
    for name, body in {
        "git": 'printf "%s\\n" "$TEST_ROOT"',
        "gh": 'echo "$*" >> "$TEST_CALLS"; exit 0',
    }.items():
        executable = bin_dir / name
        executable.write_text("#!/bin/bash\n" + body + "\n")
        executable.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        PATH=f"{bin_dir}:{env['PATH']}",
        TEST_ROOT=str(tmp_path),
        TEST_CALLS=str(calls),
        DRY_RUN="true",
    )
    result = subprocess.run(
        ["bash", str(scripts / SOURCE.name)],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    logs = list((tmp_path / "logs/compliance").glob("daily-*.log"))
    return result, logs[0].read_text(), calls.exists()


def summary(total=0, skipped=0, reviewed=0):
    """Dashboard contract: denominator=total-skipped; percent=floor(100*r/d)."""
    denominator = total - skipped
    # Alert threshold: issue 4105, Thresholds table, 2026-10-19.
    return {
        "total_commits": total,
        "skipped": skipped,
        "reviewable": denominator,
        "reviewed": reviewed,
        "unreviewed": denominator - reviewed,
        "compliance_rate": 100 * reviewed // denominator if denominator else 0,
        "threshold": 80,
        "verdict": "PASS"
        if not denominator or reviewed * 100 // denominator >= 80
        else "FAIL",
    }


@pytest.mark.parametrize("total,skipped", [(0, 0), (3, 3)])
def test_empty_denominator_never_contacts_github(tmp_path, total, skipped):
    """0/0 is undefined, including three excluded commits; no alert is warranted."""
    result, log, contacted = run_cron(tmp_path, summary(total, skipped))
    assert result.returncode == 0
    assert "No reviewable commits in window" in log
    assert "ALERT:" not in log
    assert not contacted


@pytest.mark.parametrize(
    "reviewed,severity", [(0, "critical"), (3, "high"), (5, "medium"), (8, None)]
)
def test_thresholds_preserved(tmp_path, reviewed, severity):
    """Hand calculation: r/10*100 gives 0,30,50,80%; issue 4105 thresholds."""
    result, log, contacted = run_cron(
        tmp_path, summary(10, reviewed=reviewed), dashboard_status=1 if severity else 0
    )
    assert result.returncode == 0
    assert ("ALERT:" in log) == bool(severity)
    assert contacted == bool(severity)
    if severity:
        assert f"severity: {severity}" in log


def test_nested_verdict_is_not_report_verdict(tmp_path):
    report = summary(10)
    report["stage_prompt_drift"] = {"latest_event": {"verdict": "pass"}}
    result, log, _ = run_cron(tmp_path, report, dashboard_status=1)
    assert result.returncode == 0
    assert "**Dashboard verdict:** FAIL\n\n" in log


@pytest.mark.parametrize(
    "change",
    [
        {"reviewable": 1},
        {"reviewed": True},
        {"total_commits": -1},
        {"compliance_rate": 99},
        {"unreviewed": 2},
        {"verdict": "unknown"},
    ],
)
def test_invalid_summary_cannot_become_compliance_alert(tmp_path, change):
    report = summary()
    report.update(change)
    result, log, contacted = run_cron(tmp_path, report)
    assert result.returncode != 0
    assert "Invalid dashboard summary" in log
    assert not contacted


@pytest.mark.parametrize(
    "raw", ["", "No commits in window", 'JSON Report:\n{"broken":']
)
def test_missing_or_broken_json_is_visible_failure(tmp_path, raw):
    result, log, contacted = run_cron(tmp_path, {}, raw=raw)
    assert result.returncode != 0
    assert "Invalid dashboard summary" in log
    assert not contacted


def test_dashboard_execution_failure_is_not_empty_window(tmp_path):
    result, log, contacted = run_cron(tmp_path, summary(), dashboard_status=2)
    assert result.returncode != 0
    assert "Dashboard execution failed" in log
    assert not contacted


def test_integer_percentage_truncation(tmp_path):
    """Hand calculation: floor(100*2/3)=66%, in the medium range of issue 4105."""
    result, log, contacted = run_cron(
        tmp_path, summary(3, reviewed=2), dashboard_status=1
    )
    assert result.returncode == 0
    assert "Compliance rate: 66%" in log
    assert "severity: medium" in log
    assert contacted


@pytest.mark.parametrize("payload", [[], None, {}, {"total_commits": "0"}])
def test_non_summary_json_is_rejected(tmp_path, payload):
    result, log, contacted = run_cron(tmp_path, payload)
    assert result.returncode != 0
    assert "Invalid dashboard summary" in log
    assert not contacted
