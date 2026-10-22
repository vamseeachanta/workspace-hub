"""Regression examples for the alert in issue 3855; no live publishing occurs."""

import json
import os
import runpy
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def report(total=7, skipped=7, reviewed=0, verdict="PASS"):
    """Independent arithmetic: reviewable=total-skipped; remaining=reviewable-reviewed."""
    reviewable = total - skipped
    return {
        "total_commits": total, "skipped": skipped, "reviewable": reviewable,
        "reviewed": reviewed, "unreviewed": reviewable - reviewed,
        "compliance_rate": reviewed * 100 // reviewable if reviewable else 0,
        "threshold": 80, "verdict": verdict,
        "stage_prompt_drift": {"counts": {"pass": 7}, "latest_event": {"verdict": "pass"}},
    }


def run_cron(tmp_path, payload, status=0, human="Compliance rate:    0%"):
    scripts = tmp_path / "scripts" / "enforcement"
    scripts.mkdir(parents=True)
    for name in ("compliance-cron.sh", "compliance-alert-summary.py"):
        source = ROOT / "scripts" / "enforcement" / name
        if source.exists():
            shutil.copyfile(source, scripts / name)
    output = human + "\nJSON Report:\n" + json.dumps(payload) + "\n\nReport saved to: report.json\n"
    (tmp_path / "output.txt").write_text(output)
    dashboard = scripts / "compliance-dashboard.sh"
    dashboard.write_text(f'#!/bin/bash\ncat "$FIXTURE_ROOT/output.txt"\nexit {status}\n')
    dashboard.chmod(0o755)
    bins = tmp_path / "bin"
    bins.mkdir()
    (bins / "git").write_text('#!/bin/bash\nprintf "%s\\n" "$FIXTURE_ROOT"\n')
    (bins / "gh").write_text('#!/bin/bash\necho unexpected > "$FIXTURE_ROOT/published"\nexit 1\n')
    for executable in bins.iterdir():
        executable.chmod(0o755)
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(PATH=f"{bins}:{env['PATH']}", FIXTURE_ROOT=str(tmp_path), DRY_RUN="true")
    result = subprocess.run(["bash", str(scripts / "compliance-cron.sh")],
                            env=env, cwd=tmp_path, capture_output=True, text=True, check=False)
    logs = list((tmp_path / "logs" / "compliance").glob("daily-*.log"))
    log = logs[0].read_text() if logs else ""
    assert not (tmp_path / "published").exists(), "dry run must not call publishing tools"
    return result, log


def test_skipped_commits_do_not_raise_zero_percent_alert(tmp_path):
    """Seven skipped commits: 7-7=0 reviewable; rate is inapplicable, no alert."""
    result, log = run_cron(tmp_path, report())
    assert result.returncode == 0
    assert "No reviewable commits" in log
    assert "ALERT:" not in log


@pytest.mark.parametrize("reviewed,severity", [(0, "critical"), (3, "high"), (5, "medium"), (8, None)])
def test_thresholds_use_top_level_report(tmp_path, reviewed, severity):
    """Issue 3855 thresholds: 0/10=0%, 3/10=30%, 5/10=50%, 8/10=80%."""
    payload = report(10, 0, reviewed, "PASS" if reviewed == 8 else "FAIL")
    result, log = run_cron(tmp_path, payload, 0 if reviewed == 8 else 1)
    assert result.returncode == 0
    if severity:
        assert f"severity: {severity}" in log
        assert f"**Reviewed:** {reviewed} | **Unreviewed:** {10 - reviewed}" in log
        assert "**Dashboard verdict:** FAIL\n" in log
    else:
        assert "ALERT:" not in log


@pytest.mark.parametrize("mutation,status", [({"reviewable": 1}, 0),
                                             ({"compliance_rate": 99}, 0),
                                             ({"verdict": "FAIL"}, 0),
                                             ({"reviewed": True}, 0),
                                             ({}, 2),
                                             ({"skipped": -1}, 0),
                                             ({"threshold": 101}, 0),
                                             ({"unreviewed": 1}, 0),
                                             ({"reviewed": 0.0}, 0),
                                             ({"total_commits": None}, 0)])
def test_inconsistent_reports_fail_without_alert(tmp_path, mutation, status):
    payload = report()
    payload.update(mutation)
    result, log = run_cron(tmp_path, payload, status)
    assert result.returncode != 0
    assert "ERROR:" in log
    assert "ALERT:" not in log


def test_malformed_report_fails_without_alert(tmp_path):
    result, log = run_cron(tmp_path, "not an object")
    assert result.returncode != 0
    assert "ERROR:" in log


@pytest.mark.parametrize("total,skipped,reviewed,rate", [(0, 0, 0, 0), (3, 0, 2, 66)])
def test_empty_and_fractional_windows(tmp_path, total, skipped, reviewed, rate):
    """N=0 needs no alert; two reviewed of three gives floor(200/3)=66 percent."""
    payload = report(total, skipped, reviewed, "FAIL" if total else "PASS")
    result, log = run_cron(tmp_path, payload, 1 if total else 0)
    assert result.returncode == 0
    if total:
        assert f"Compliance rate: {rate}%" in log
        assert "severity: medium" in log
    else:
        assert "No reviewable commits" in log
        assert "ALERT:" not in log


@pytest.mark.parametrize("rate,severity", [(29, "critical"), (49, "high"), (79, "medium")])
def test_just_below_boundaries(tmp_path, rate, severity):
    """With 100 reviewable commits, the count reviewed equals its percentage."""
    result, log = run_cron(tmp_path, report(100, 0, rate, "FAIL"), 1)
    assert result.returncode == 0
    assert f"severity: {severity}" in log


@pytest.mark.parametrize("output", ["", "Compliance rate: 0%", "JSON Report:\n{",
                                    "JSON Report:\n{}\nJSON Report:\n{}"])
def test_missing_truncated_or_ambiguous_json_is_rejected(output):
    summarize = runpy.run_path(str(ROOT / "scripts/enforcement/compliance-alert-summary.py"))["summarize"]
    with pytest.raises(ValueError):
        summarize(output, 0)


def test_dashboard_failure_status_is_required():
    """A zero-of-ten FAIL report shall be accompanied by dashboard exit status one."""
    summarize = runpy.run_path(str(ROOT / "scripts/enforcement/compliance-alert-summary.py"))["summarize"]
    with pytest.raises(ValueError, match="exit status"):
        summarize("JSON Report:\n" + json.dumps(report(10, 0, 0, "FAIL")), 0)
