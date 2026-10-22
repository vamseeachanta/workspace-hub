"""Regression cases for the alert reproduced in issue #3794 (2026-08-03).

Expected rates use independent integer arithmetic: floor(100 * reviewed /
reviewable). Thresholds come from that issue's Thresholds table, not a standard.
All repositories, history, and publishing commands below are synthetic.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts/enforcement"


def report(reviewed=2, unreviewed=1, skipped=7):
    """Hand calculation: 2 / (2 + 1) * 100 = 66.6…; integer rate = 66."""
    reviewable = reviewed + unreviewed
    rate = reviewed * 100 // reviewable if reviewable else 0
    return {
        "total_commits": reviewable + skipped,
        "skipped": skipped,
        "reviewable": reviewable,
        "reviewed": reviewed,
        "unreviewed": unreviewed,
        "compliance_rate": rate,
        "threshold": 80,  # Issue #3794 (2026), Thresholds table.
        "verdict": "FAIL" if reviewable and rate < 80 else "PASS",
        "stage_prompt_drift": {"latest_event": {"verdict": "pass"}},
    }


def output(payload):
    return "Compliance report\nJSON Report:\n" + json.dumps(payload) + "\n\nReport saved to: report.json\n"


def parse(text):
    return subprocess.run(
        ["python3", str(SCRIPTS / "compliance_report.py")], input=text,
        capture_output=True, text=True, check=False,
    )


@pytest.mark.parametrize(
    ("reviewed", "unreviewed", "severity"),
    [(0, 10, "critical"), (29, 71, "critical"), (3, 7, "high"),
     (49, 51, "high"), (5, 5, "medium"), (79, 21, "medium"),
     (8, 2, "pass"), (10, 0, "pass"), (0, 0, "not_evaluated")],
)
def test_structured_thresholds(reviewed, unreviewed, severity):
    """Hand counts give 0, 29, 30, 49, 50, 79, 80, 100%; empty is undefined.

    Boundary actions: issue #3794 (2026), Thresholds table (30/50/80%).
    """
    result = parse(output(report(reviewed, unreviewed)))
    assert result.returncode == 0, result.stderr
    fields = result.stdout.strip().split("\t")
    assert fields[-1] == severity
    assert fields[-2] == report(reviewed, unreviewed)["verdict"]


def test_nested_verdict_does_not_contaminate_metrics():
    result = parse(output(report()))
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().split("\t") == ["66", "10", "2", "1", "3", "FAIL", "medium"]


@pytest.mark.parametrize("field,value", [
    ("reviewed", -1), ("reviewed", True), ("reviewed", "2"),
    ("unreviewed", 2), ("skipped", 8), ("reviewable", 4),
    ("total_commits", 11), ("compliance_rate", 67),
    ("threshold", 101), ("verdict", "PASS"),
])
def test_invalid_report_is_rejected(field, value):
    payload = report()
    payload[field] = value
    result = parse(output(payload))
    assert result.returncode != 0
    assert not result.stdout
    assert "Invalid compliance report" in result.stderr


@pytest.mark.parametrize("text", [
    "", "No commits in window", "JSON Report:\n{}", "JSON Report:\n{",
    'JSON Report:\n{"reviewed":2,"reviewed":3}',
    output(report()) + output(report()),
    output(report()).split("\n\nReport saved to:")[0] + '\n{"verdict":"PASS"}',
    "JSON Report:\n[]",
])
def test_incomplete_or_ambiguous_output_is_rejected(text):
    result = parse(text)
    assert result.returncode != 0
    assert not result.stdout


def fake_commands(tmp_path):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    git = bindir / "git"
    git.write_text('''#!/usr/bin/env bash
if [[ "$*" == *rev-parse* ]]; then
  printf '%s\\n' "$FIXTURE_ROOT"
elif [[ "$*" == *--since=* ]]; then
  [[ "${FAIL_HISTORY:-0}" == 1 ]] && exit 2
  cat "$FIXTURE_COMMITS"
elif [[ "$*" == *--format=* ]]; then
  echo 'implementation without evidence'
else
  exit 1
fi
''')
    gh = bindir / "gh"
    gh.write_text('#!/usr/bin/env bash\necho called >> "$GH_CALLS"\nexit 97\n')
    git.chmod(0o755)
    gh.chmod(0o755)
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        env.pop(key, None)
    env.update({
        "PATH": str(bindir) + os.pathsep + env["PATH"],
        "FIXTURE_ROOT": str(tmp_path),
        "FIXTURE_COMMITS": str(tmp_path / "commits.txt"),
        "GH_CALLS": str(tmp_path / "gh-calls.txt"),
        "COMPLIANCE_REPORTS_DIR": str(tmp_path / "reports"),
        "DRY_RUN": "true",
    })
    return env


@pytest.mark.parametrize("subject,skipped", [
    ("ci: frozen installs", 1), ("ci(build): frozen installs", 1),
    ("docs!: update guide", 1), ("docs(api)!: update guide", 1),
    ("Merge branch 'topic'", 1), ('Revert "change"', 1),
    ("feat(skill): add guide", 1), ("feat(wiki): add guide", 1),
    ("feat(skillful): add code", 0), ("fix: repair code", 0),
    ("feat(core)!: change API", 0), ("untyped implementation", 0),
])
def test_dashboard_classification(tmp_path, subject, skipped):
    env = fake_commands(tmp_path)
    (tmp_path / "commits.txt").write_text("a" * 40 + " " + subject + "\n")
    result = subprocess.run(["bash", str(SCRIPTS / "compliance-dashboard.sh")],
                            cwd=tmp_path, env=env, text=True, capture_output=True, check=False)
    blob = result.stdout.split("JSON Report:\n", 1)[1]
    payload, _ = json.JSONDecoder().raw_decode(blob)
    assert payload["skipped"] == skipped
    assert payload["reviewable"] == 1 - skipped
    assert payload["unreviewed"] == 1 - skipped
    assert result.returncode == 1 - skipped


def run_cron(tmp_path, text, status=0):
    env = fake_commands(tmp_path)
    scriptdir = tmp_path / "scripts/enforcement"
    scriptdir.mkdir(parents=True)
    shutil.copy(SCRIPTS / "compliance-cron.sh", scriptdir)
    parser = SCRIPTS / "compliance_report.py"
    if parser.exists():
        shutil.copy(parser, scriptdir)
    payload_path = tmp_path / "dashboard.txt"
    payload_path.write_text(text)
    env["DASHBOARD_FIXTURE"] = str(payload_path)
    dashboard = scriptdir / "compliance-dashboard.sh"
    dashboard.write_text('#!/usr/bin/env bash\ncat "$DASHBOARD_FIXTURE"\nexit ' + str(status) + '\n')
    dashboard.chmod(0o755)
    result = subprocess.run(["bash", str(scriptdir / "compliance-cron.sh")],
                            cwd=tmp_path, env=env, capture_output=True, text=True, check=False)
    assert not (tmp_path / "gh-calls.txt").exists(), "dry run must make no GitHub calls"
    return result, "\n".join(p.read_text() for p in (tmp_path / "reports").glob("*.log"))


@pytest.mark.parametrize("skipped", [0, 6])
def test_cron_does_not_alert_for_empty_reviewable_window(tmp_path, skipped):
    result, log = run_cron(tmp_path, output(report(0, 0, skipped)))
    assert result.returncode == 0, result.stderr
    assert "No reviewable commits" in log
    assert "ALERT:" not in log


def test_cron_dry_run_contains_single_top_level_verdict(tmp_path):
    result, log = run_cron(tmp_path, output(report()), status=1)
    assert result.returncode == 0, result.stderr
    assert "[DRY RUN]" in log
    assert "**Dashboard verdict:** FAIL\n" in log
    assert "FAIL\npass" not in log


@pytest.mark.parametrize("text,status", [("No commits in window", 0), (output(report()), 2)])
def test_cron_does_not_hide_dashboard_errors(tmp_path, text, status):
    result, log = run_cron(tmp_path, text, status)
    assert result.returncode != 0
    assert "ERROR:" in log


def test_dashboard_does_not_hide_history_errors(tmp_path):
    env = fake_commands(tmp_path)
    env["FAIL_HISTORY"] = "1"
    result = subprocess.run(["bash", str(SCRIPTS / "compliance-dashboard.sh")],
                            cwd=tmp_path, env=env, capture_output=True, text=True, check=False)
    assert result.returncode != 0
    assert "JSON Report:" not in result.stdout


@pytest.mark.parametrize("reviewed,unreviewed,status", [(8, 2, 0), (2, 1, 0), (8, 2, 1)])
def test_cron_checks_exit_status_against_verdict(tmp_path, reviewed, unreviewed, status):
    """Hand rates are 80% (PASS) and floor(200/3)=66% (FAIL)."""
    result, log = run_cron(tmp_path, output(report(reviewed, unreviewed)), status)
    expected_ok = reviewed == 8 and status == 0
    assert (result.returncode == 0) is expected_ok
    assert ("ERROR:" not in log) is expected_ok


def test_dashboard_and_cron_integrate_in_dry_run(tmp_path):
    """One exempt subject and one implementation: 0/1 => 0%, critical.

    The one real candidate remains visible; fixing exemptions cannot hide it.
    """
    env = fake_commands(tmp_path)
    scriptdir = tmp_path / "scripts/enforcement"
    scriptdir.mkdir(parents=True)
    for name in ("compliance-dashboard.sh", "compliance-cron.sh", "compliance_report.py"):
        shutil.copy(SCRIPTS / name, scriptdir)
    (tmp_path / "commits.txt").write_text(
        "a" * 40 + " ci: frozen installs\n" + "b" * 40 + " fix(core): repair code\n"
    )
    result = subprocess.run(["bash", str(scriptdir / "compliance-cron.sh")],
                            cwd=tmp_path, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "gh-calls.txt").exists()
    log = next((tmp_path / "reports").glob("daily-*.log")).read_text()
    assert "**Total commits:** 2 | **Reviewed:** 0 | **Unreviewed:** 1" in log
    assert "bbbbbbbb fix(core): repair code" in log
    assert "aaaaaaaa ci: frozen installs" not in log
    assert "severity: critical" in log
