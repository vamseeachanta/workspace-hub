"""Alert regressions; synthetic counts use the dashboard's integer-rate definition.

Hand calculation: seven skipped commits give 7 - 7 = 0 reviewable commits,
so the rate is undefined for alerting. With five reviewable commits and one
reviewed commit, floor(100 * 1 / 5) = 20 percent, below the critical boundary.
Policy source: compliance-cron.sh, Alert thresholds and issue 3882 (2026).
"""

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts/enforcement"


def load_parser():
    spec = importlib.util.spec_from_file_location(
        "compliance_alert_report", SCRIPTS / "compliance_alert_report.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse_report


def report(**changes):
    payload = {
        "total_commits": 5, "skipped": 0, "reviewable": 5, "reviewed": 1,
        "unreviewed": 4, "compliance_rate": 20, "threshold": 80, "verdict": "FAIL",
        "stage_prompt_drift": {
            "counts": {"pass": 1}, "latest_event": {"verdict": "pass"},
        },
    }
    payload.update(changes)
    return payload


def output(payload):
    return "Compliance rate:    0%\nJSON Report:\n" + json.dumps(payload) + "\n\nReport saved to: report.json\n"


def test_top_level_fields_only():
    parsed = load_parser()(output(report()))
    assert parsed["compliance_rate"] == 20
    assert parsed["verdict"] == "FAIL"


@pytest.mark.parametrize("changes", [
    {"total_commits": -1}, {"reviewed": True}, {"reviewed": "1"},
    {"reviewed": 1.0}, {"unreviewed": 0}, {"skipped": 1},
    {"reviewable": 0}, {"compliance_rate": 21}, {"threshold": 101},
    {"threshold": -1}, {"verdict": "PASS"}, {"verdict": "pass"},
])
def test_inconsistent_reports_rejected(changes):
    with pytest.raises((ValueError, TypeError)):
        load_parser()(output(report(**changes)))


@pytest.mark.parametrize("field", [
    "total_commits", "skipped", "reviewable", "reviewed", "unreviewed",
    "compliance_rate", "threshold", "verdict",
])
def test_missing_fields_rejected(field):
    payload = report()
    del payload[field]
    with pytest.raises((ValueError, TypeError)):
        load_parser()(output(payload))


@pytest.mark.parametrize("text", [
    "Compliance rate: 0%", "JSON Report:\n{broken}", "JSON Report:\n[]",
    'JSON Report:\n{"reviewed": 1, "reviewed": 2}',
    "JSON Report:\n{}\nJSON Report:\n{}",
])
def test_invalid_transport_rejected(text):
    with pytest.raises((ValueError, TypeError)):
        load_parser()(text)


def run_cron(tmp_path, payload, dashboard_rc=0):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("compliance-cron.sh", "compliance_alert_report.py"):
        shutil.copyfile(SCRIPTS / name, scripts / name)
    dashboard = scripts / "compliance-dashboard.sh"
    dashboard.write_text('#!/bin/bash\ncat "$FAKE_REPORT"\nexit "$FAKE_RC"\n')
    dashboard.chmod(0o755)
    fixture = tmp_path / "report.txt"
    fixture.write_text(output(payload))
    binaries = tmp_path / "bin"
    binaries.mkdir()
    for name, body in {
        "git": 'printf "%s\\n" "$FAKE_ROOT"',
        "gh": 'echo "$*" >> "$FAKE_CALLS"; echo "[]"',
    }.items():
        executable = binaries / name
        executable.write_text("#!/bin/bash\n" + body + "\n")
        executable.chmod(0o755)
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    env.update(
        PATH=str(binaries) + os.pathsep + env["PATH"],
        FAKE_ROOT=str(tmp_path), FAKE_REPORT=str(fixture),
        FAKE_RC=str(dashboard_rc), FAKE_CALLS=str(tmp_path / "calls"),
        DRY_RUN="true",
    )
    result = subprocess.run(
        ["bash", str(scripts / "compliance-cron.sh")],
        env=env, text=True, capture_output=True, check=False,
    )
    logs = list((tmp_path / "logs/compliance").glob("daily-*.log"))
    return result, logs[0].read_text(), tmp_path / "calls"


@pytest.mark.parametrize("total", [0, 7])
def test_no_reviewable_commits_do_not_alert(tmp_path, total):
    result, log, calls = run_cron(tmp_path, report(
        total_commits=total, skipped=total, reviewable=0, reviewed=0,
        unreviewed=0, compliance_rate=0, verdict="PASS",
    ))
    assert result.returncode == 0
    assert "No reviewable commits" in log
    assert "ALERT:" not in log
    assert not calls.exists()


@pytest.mark.parametrize("rate,severity", [
    (0, "critical"), (29, "critical"), (30, "high"), (49, "high"),
    (50, "medium"), (79, "medium"), (80, None), (100, None),
])
def test_threshold_boundaries(tmp_path, rate, severity):
    """100 reviewable commits: reviewed * 100 / 100 = reviewed percent.

    Expected severities come from issue 3882's Thresholds table (2026).
    """
    result, log, calls = run_cron(tmp_path, report(
        total_commits=100, reviewable=100, reviewed=rate, unreviewed=100-rate,
        compliance_rate=rate, verdict="FAIL" if rate < 80 else "PASS",
    ), dashboard_rc=int(rate < 80))
    assert result.returncode == 0, result.stderr
    if severity:
        assert f"severity: {severity}" in log
        assert "**Dashboard verdict:** FAIL\n" in log
        assert f"**Reviewed:** {rate} | **Unreviewed:** {100-rate}" in log
        assert "label create" not in calls.read_text()
        assert "issue create" not in calls.read_text()
        assert "issue comment" not in calls.read_text()
    else:
        assert "PASS:" in log
        assert not calls.exists()


@pytest.mark.parametrize("changes,rc", [({"unreviewed": 0}, 1), ({}, 2), ({}, 0)])
def test_invalid_report_or_dashboard_failure_stops_before_github(tmp_path, changes, rc):
    result, log, calls = run_cron(tmp_path, report(**changes), dashboard_rc=rc)
    assert result.returncode == 1
    assert "ERROR:" in log
    assert not calls.exists()
