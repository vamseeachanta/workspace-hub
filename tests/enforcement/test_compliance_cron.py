"""Alert regressions; synthetic counts are hand-calculated, not review evidence.

Sources: issue 3830, Thresholds (2026-09-07), for severity limits; the shipped
compliance-dashboard.sh main function for count identities and integer rates.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts" / "enforcement"


def report(reviewed=0, unreviewed=0, skipped=7):
    """Dashboard formula: floor(100 * reviewed / eligible), or zero if empty."""
    eligible = reviewed + unreviewed
    rate = reviewed * 100 // eligible if eligible else 0
    return {
        "total_commits": eligible + skipped,
        "skipped": skipped,
        "reviewable": eligible,
        "reviewed": reviewed,
        "unreviewed": unreviewed,
        "compliance_rate": rate,
        "threshold": 80,
        "verdict": "FAIL" if eligible and rate < 80 else "PASS",
        "stage_prompt_drift": {"latest_event": {"verdict": "pass"}},
    }


def invoke(tmp_path, payload, status=None, raw=None, commits=None):
    """Copy scripts to a disposable root; Git and GitHub calls are stubs."""
    scripts = tmp_path / "scripts" / "enforcement"
    scripts.mkdir(parents=True)
    for name in ("compliance-cron.sh", "compliance_metrics.py"):
        source = SCRIPTS / name
        if source.exists():
            shutil.copyfile(source, scripts / name)
    output = raw if raw is not None else (
        'Compliance rate:    0%\nVerdict: PASS\nJSON Report:\n'
        + json.dumps(payload) + '\n\nReport saved to: report.json\n'
    )
    (tmp_path / "output.txt").write_text(output)
    if status is None:
        status = int(payload["verdict"] == "FAIL")
    dashboard = scripts / "compliance-dashboard.sh"
    dashboard.write_text(
        '#!/usr/bin/env bash\ncat "$FIXTURE_ROOT/output.txt"\n'
        f'exit {status}\n'
    )
    dashboard.chmod(0o755)
    if commits is not None:
        shutil.copyfile(SCRIPTS / "compliance-dashboard.sh", dashboard)
        (tmp_path / "commits.txt").write_text(commits)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, body in {
        "git": 'case "$*" in *--show-toplevel*) '
               'printf "%s\\n" "$FIXTURE_ROOT";; *) '
               'cat "$FIXTURE_ROOT/commits.txt";; esac',
        "gh": 'echo called > "$FIXTURE_ROOT/gh-called"; '
              'echo unexpected-gh-call >&2; exit 99',
    }.items():
        tool = bin_dir / name
        tool.write_text('#!/usr/bin/env bash\n' + body + '\n')
        tool.chmod(0o755)
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_")}
    env.update(PATH=f"{bin_dir}{os.pathsep}{env['PATH']}",
               FIXTURE_ROOT=str(tmp_path), DRY_RUN="true")
    result = subprocess.run(
        ["bash", str(scripts / "compliance-cron.sh")], cwd=tmp_path,
        env=env, text=True, capture_output=True, check=False,
    )
    assert not (tmp_path / "gh-called").exists(), "dry run called GitHub"
    logs = list((tmp_path / "logs" / "compliance").glob("daily-*.log"))
    return result, logs[0].read_text() if logs else ""


@pytest.mark.parametrize("count", [0, 7])
def test_shipped_dashboard_empty_population(tmp_path, count):
    """Seven docs(core) commits give total=7, skipped=7 and reviewable=0."""
    commits = "".join(f"{index:040x} docs(core): update guide\n"
                      for index in range(count))
    result, log = invoke(tmp_path, report(), commits=commits)
    assert result.returncode == 0
    assert "No reviewable commits" in log
    assert "ALERT:" not in log
    assert f'"total_commits": {count}' in log
    assert '"reviewable": 0' in log


@pytest.mark.parametrize("skipped", [0, 7])
def test_empty_denominator_does_not_alert(tmp_path, skipped):
    """Issue 3830: seven skipped -> eligible=7-7=0; no rate is evaluable."""
    result, log = invoke(tmp_path, report(skipped=skipped))
    assert result.returncode == 0
    assert "No reviewable commits" in log
    assert "ALERT:" not in log
    assert "unexpected-gh-call" not in result.stderr


@pytest.mark.parametrize("reviewed,unreviewed,severity", [
    (0, 7, "critical"), (29, 71, "critical"), (30, 70, "high"),
    (49, 51, "high"), (50, 50, "medium"), (79, 21, "medium"),
    (2, 1, "medium"),
])
def test_alert_boundaries_and_single_verdict(tmp_path, reviewed, unreviewed, severity):
    """Issue 3830 thresholds: <30 critical, <50 high, <80 medium.

    Each boundary has 100 eligible, so reviewed/100*100 equals reviewed.
    The zero case has 0/7*100=0; floor(200/3)=66 for the fractional case.
    Nested 'pass' must not enter the verdict.
    """
    result, log = invoke(tmp_path, report(reviewed, unreviewed))
    assert result.returncode == 0
    assert f"severity: {severity}" in log
    assert "[DRY RUN] Would create/update issue:" in log
    assert "**Dashboard verdict:** FAIL\n" in log
    assert "**Dashboard verdict:** FAIL\npass" not in log
    assert "unexpected-gh-call" not in result.stderr


@pytest.mark.parametrize("reviewed,unreviewed", [(80, 20), (100, 0), (4, 1)])
def test_passing_threshold(tmp_path, reviewed, unreviewed):
    """80/100 and 4/5 yield 80%; 100/100 yields 100%; issue 3830 passes >=80."""
    result, log = invoke(tmp_path, report(reviewed, unreviewed))
    assert result.returncode == 0
    assert "PASS:" in log
    assert "ALERT:" not in log


@pytest.mark.parametrize("changes", [
    {"reviewable": 1}, {"reviewed": -1}, {"skipped": True},
    {"unreviewed": "0"}, {"compliance_rate": 30}, {"verdict": "FAIL"},
    {"threshold": 101}, {"total_commits": 8}, {"threshold": 80.0},
])
def test_inconsistent_metrics_fail_without_alert(tmp_path, changes):
    payload = report()
    payload.update(changes)
    result, log = invoke(tmp_path, payload, status=0)
    assert result.returncode != 0
    assert "ERROR:" in log
    assert "ALERT:" not in log


@pytest.mark.parametrize("raw", [
    "No commits in window", "JSON Report:\n{broken}",
    'JSON Report:\n{"total_commits":0,"total_commits":7}',
    'JSON Report:\n[]',
])
def test_missing_or_invalid_json_fails(tmp_path, raw):
    result, log = invoke(tmp_path, report(), raw=raw)
    assert result.returncode != 0
    assert "ERROR:" in log


@pytest.mark.parametrize("payload,status", [(report(), 2), (report(), 1),
                                               (report(0, 7), 0)])
def test_dashboard_status_must_match_verdict(tmp_path, payload, status):
    result, log = invoke(tmp_path, payload, status=status)
    assert result.returncode != 0
    assert "ERROR:" in log
    assert "ALERT:" not in log
