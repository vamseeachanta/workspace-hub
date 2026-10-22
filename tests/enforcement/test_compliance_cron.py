"""Alert regression cases for issue #3927 and its Thresholds (2026-09-28).

All counts are synthetic inputs. Expected percentages are hand calculations:
reviewed * 100 // reviewable, as specified by compliance-dashboard.sh, main.
The policy boundaries come from issue #3927, Thresholds, and issue #2031's
implementation summary (2026-04-09); they are operational policy, not standards.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "enforcement"


def report(*, reviewed=0, unreviewed=0, skipped=0, threshold=80):
    """Independent fixture: e.g. 1 reviewed + 2 unreviewed -> 100 // 3 = 33%."""
    reviewable = reviewed + unreviewed
    rate = reviewed * 100 // reviewable if reviewable else 0
    return {
        "total_commits": reviewable + skipped,
        "skipped": skipped,
        "reviewable": reviewable,
        "reviewed": reviewed,
        "unreviewed": unreviewed,
        "compliance_rate": rate,
        "threshold": threshold,
        "verdict": "FAIL" if reviewable and rate < threshold else "PASS",
        # Regression: a nested verdict must never be read as the report verdict.
        "stage_prompt_drift": {"latest_event": {"verdict": "pass"}},
    }


def dashboard_output(payload):
    return (
        f"Compliance rate:    {payload['compliance_rate']}% (threshold: 80%)\n"
        "Unreviewed commits:\n  - abcdef12 fix(core): synthetic change\n\n"
        "JSON Report:\n" + json.dumps(payload) + "\n\nReport saved to: report.json\n"
    )


def evaluate(text, status=0):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "compliance_alert.py"),
         "--dashboard-status", str(status)],
        input=text, capture_output=True, text=True, check=False,
    )


@pytest.mark.parametrize("skipped", [0, 1, 5])
def test_no_reviewable_commits_are_not_an_alert(skipped):
    """0 / 0 is undefined, including when all 1 or 5 commits are skipped."""
    result = evaluate(dashboard_output(report(skipped=skipped)))
    assert result.returncode == 0
    assert result.stdout.split()[0] == "EMPTY"


@pytest.mark.parametrize(
    "reviewed,unreviewed,expected,severity",
    [(0, 1, 0, "critical"), (29, 71, 29, "critical"),
     (3, 7, 30, "high"), (49, 51, 49, "high"),
     (1, 1, 50, "medium"), (79, 21, 79, "medium"),
     (4, 1, 80, "none"), (1, 0, 100, "none"),
     (1, 2, 33, "high")],
)
def test_policy_boundaries(reviewed, unreviewed, expected, severity):
    """Hand calculations: 29/100=29%, 3/10=30%, 49/100=49%, 1/2=50%,
    79/100=79%, 4/5=80%, 1/1=100%, and floor(100/3)=33%.
    The zero-review case is 0/1=0%, distinct from an empty denominator.
    """
    payload = report(reviewed=reviewed, unreviewed=unreviewed)
    result = evaluate(dashboard_output(payload), int(payload["verdict"] == "FAIL"))
    assert result.returncode == 0
    fields = result.stdout.split()
    assert fields[0] == ("PASS" if severity == "none" else "ALERT")
    assert fields[1] == str(expected)
    assert fields[-1] == severity


def test_uses_dashboard_threshold():
    """4/5*100=80%; a supplied 90% threshold requires an alert."""
    result = evaluate(dashboard_output(report(reviewed=4, unreviewed=1, threshold=90)), 1)
    assert result.returncode == 0
    assert result.stdout.split()[0] == "ALERT"
    assert result.stdout.split()[-2:] == ["90", "medium"]


@pytest.mark.parametrize("field,value", [
    ("reviewable", -1), ("total_commits", 7), ("reviewed", True),
    ("unreviewed", "1"), ("skipped", 0.0), ("compliance_rate", 101),
    ("compliance_rate", 9), ("threshold", 101), ("verdict", "pass"),
    ("verdict", "PASS"),
])
def test_invalid_counts_rates_and_verdicts_are_not_evaluated(field, value):
    """For 0 reviewed / 1 reviewable the only coherent rate/verdict is 0/FAIL."""
    payload = report(unreviewed=1)
    payload[field] = value
    result = evaluate(dashboard_output(payload), 1)
    assert result.returncode != 0
    assert "NOT_EVALUATED" in result.stderr
    assert not result.stdout


@pytest.mark.parametrize("text", [
    "", "Compliance rate:    0%\n", 'JSON Report:\n{"reviewed":',
    'JSON Report:\n[]', 'JSON Report:\n{"reviewed":0,"reviewed":1}',
    'JSON Report:\n{}\nJSON Report:\n{}',
])
def test_missing_malformed_and_ambiguous_reports_are_not_evaluated(text):
    result = evaluate(text)
    assert result.returncode != 0
    assert "NOT_EVALUATED" in result.stderr


@pytest.mark.parametrize("status", [0, 2, 127])
def test_dashboard_failure_is_not_hidden(status):
    """A FAIL verdict must have status 1; status 0, 2 or 127 is inconsistent."""
    result = evaluate(dashboard_output(report(unreviewed=1)), status)
    assert result.returncode != 0
    assert "NOT_EVALUATED" in result.stderr


def run_cron(tmp_path, payload, *, status=None, dry_run=False, existing="", raw=None, real_dashboard=False):
    scripts = tmp_path / "repo" / "scripts" / "enforcement"
    scripts.mkdir(parents=True)
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env["HOME"] = str(tmp_path / "user")
    subprocess.run(["git", "init", str(tmp_path / "repo")], env=env,
                   check=True, capture_output=True, text=True)
    shutil.copy2(SCRIPTS / "compliance-cron.sh", scripts)
    helper = SCRIPTS / "compliance_alert.py"
    if helper.exists():
        shutil.copy2(helper, scripts)
    (scripts / "compliance-dashboard.sh").write_text(
        '#!/usr/bin/env bash\ncat "$DASHBOARD_FIXTURE"\nexit "$FIXTURE_EXIT_STATUS"\n'
    )
    (scripts / "compliance-dashboard.sh").chmod(0o755)
    if real_dashboard:
        shutil.copy2(SCRIPTS / "compliance-dashboard.sh", scripts)
    fixture = tmp_path / "dashboard.txt"
    fixture.write_text(raw if raw is not None else dashboard_output(payload))
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    calls = tmp_path / "calls.txt"
    (fake_bin / "gh").write_text(
        '#!/usr/bin/env bash\nprintf "%s\\n" "$*" >> "$GH_CALLS"\n'
        'if [[ "$1 $2" == "issue list" ]]; then echo "$EXISTING_ISSUE"; fi\n'
    )
    (fake_bin / "gh").chmod(0o755)
    env.update({
        "PATH": str(fake_bin) + os.pathsep + env["PATH"],
        "DASHBOARD_FIXTURE": str(fixture),
        "FIXTURE_EXIT_STATUS": str(int(payload["verdict"] == "FAIL") if status is None else status),
        "GH_CALLS": str(calls), "EXISTING_ISSUE": existing,
        "DRY_RUN": "true" if dry_run else "false",
    })
    result = subprocess.run(["bash", str(scripts / "compliance-cron.sh")],
                            cwd=tmp_path / "repo", env=env,
                            capture_output=True, text=True, check=False)
    return result, calls.read_text() if calls.exists() else ""


@pytest.mark.parametrize("skipped", [0, 1])
def test_cron_suppresses_empty_and_skip_only_alerts(tmp_path, skipped):
    result, calls = run_cron(tmp_path, report(skipped=skipped))
    assert result.returncode == 0
    assert "No reviewable commits" in result.stdout
    assert calls == ""


def test_cron_pass_has_no_github_calls(tmp_path):
    result, calls = run_cron(tmp_path, report(reviewed=4, unreviewed=1))
    assert result.returncode == 0
    assert "PASS:" in result.stdout
    assert calls == ""


def test_cron_dry_run_has_no_github_calls(tmp_path):
    result, calls = run_cron(tmp_path, report(unreviewed=1), dry_run=True)
    assert result.returncode == 0
    assert "[DRY RUN]" in result.stdout
    assert calls == ""


@pytest.mark.parametrize("existing,operation", [("", "create"), ("123", "comment")])
def test_cron_alert_preserves_details_and_deduplication(tmp_path, existing, operation):
    result, calls = run_cron(tmp_path, report(unreviewed=1), existing=existing)
    assert result.returncode == 0
    assert f"issue {operation}" in calls
    assert "priority:critical" in calls
    assert "abcdef12 fix(core): synthetic change" in calls
    assert "**Reviewed:** 0 | **Unreviewed:** 1" in calls
    if operation == "create":
        assert "**Dashboard verdict:** FAIL\n" in calls
        assert "**Dashboard verdict:** FAIL\npass" not in calls


@pytest.mark.parametrize("raw,status", [("not a report", 0), (None, 2)])
def test_cron_invalid_or_failed_dashboard_does_not_publish(tmp_path, raw, status):
    result, calls = run_cron(tmp_path, report(unreviewed=1), raw=raw, status=status)
    assert result.returncode != 0
    assert "NOT_EVALUATED" in result.stdout + result.stderr
    assert calls == ""


@pytest.mark.parametrize("constant", ["NaN", "Infinity", "-Infinity"])
def test_non_json_constants_are_rejected(constant):
    """JSON has no nonfinite numbers, even in unused nested metadata."""
    text = dashboard_output(report()).replace('"verdict": "pass"', f'"value": {constant}')
    result = evaluate(text)
    assert result.returncode != 0
    assert "NOT_EVALUATED" in result.stderr


def test_error_does_not_repeat_raw_input():
    result = evaluate('JSON Report:\n{"PRIVATE_PAYLOAD": invalid}')
    assert result.returncode != 0
    assert "PRIVATE_PAYLOAD" not in result.stderr


def test_threshold_below_policy_boundaries_can_pass():
    """1/4*100=25%; a supplied threshold of 20% passes despite being below 30%."""
    result = evaluate(dashboard_output(report(reviewed=1, unreviewed=3, threshold=20)))
    assert result.returncode == 0
    assert result.stdout.split()[0] == "PASS"


def test_real_dashboard_empty_window(tmp_path):
    result, calls = run_cron(tmp_path, report(), real_dashboard=True)
    assert result.returncode == 0
    assert "No reviewable commits" in result.stdout
    assert calls == ""
