"""Cron regressions with synthetic counts and independent integer arithmetic."""

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PARSER = ROOT / "scripts/enforcement/compliance_report.py"


def load_parser():
    spec = importlib.util.spec_from_file_location("compliance_report", PARSER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def report(reviewed=0, unreviewed=1, skipped=8):
    """Hand calculation: default 0/(9-8)*100 = 0%; 1/3*100 floors to 33%."""
    reviewable = reviewed + unreviewed
    rate = reviewed * 100 // reviewable if reviewable else 0
    # Source: issue threshold table and compliance-dashboard.sh default threshold.
    return {"total_commits": reviewable + skipped, "skipped": skipped,
            "reviewable": reviewable, "reviewed": reviewed, "unreviewed": unreviewed,
            "compliance_rate": rate, "threshold": 80,
            "verdict": "FAIL" if reviewable and rate < 80 else "PASS",
            "stage_prompt_drift": {"latest_event": {"verdict": "pass"}}}


def output(payload):
    return "Compliance rate: 99%\nJSON Report:\n" + json.dumps(payload) + "\n\nReport saved to: report.json\n"


def test_top_level_json_only():
    parsed = load_parser().parse_report(output(report()))
    assert parsed["verdict"] == "FAIL"
    assert parsed["compliance_rate"] == 0


@pytest.mark.parametrize("reviewed,unreviewed,expected", [(1, 2, 33), (4, 1, 80), (0, 0, 0)])
def test_hand_calculated_rates(reviewed, unreviewed, expected):
    """Synthetic examples: floor(100/3)=33, 400/5=80, empty denominator stored as 0."""
    assert load_parser().parse_report(output(report(reviewed, unreviewed)))["compliance_rate"] == expected


@pytest.mark.parametrize("field,value", [
    ("total_commits", 10), ("reviewable", 2), ("reviewed", -1),
    ("unreviewed", True), ("skipped", "8"), ("compliance_rate", 99),
    ("threshold", 101), ("verdict", "PASS"),
])
def test_reject_inconsistent_report(field, value):
    payload = report()
    payload[field] = value
    with pytest.raises((TypeError, ValueError)):
        load_parser().parse_report(output(payload))


@pytest.mark.parametrize("text", ["", "No commits in window", 'JSON Report:\n{"verdict":"PASS"}',
                                  'JSON Report:\n[]', 'JSON Report:\n{bad}'])
def test_reject_missing_or_malformed(text):
    with pytest.raises((TypeError, ValueError)):
        load_parser().parse_report(text)


def run_cron(tmp_path, payload, status=1):
    """Only stub GitHub reads are allowed; a mutation makes the test fail."""
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("compliance-cron.sh", "compliance_report.py"):
        shutil.copyfile(ROOT / "scripts/enforcement" / name, scripts / name)
    dashboard = scripts / "compliance-dashboard.sh"
    dashboard.write_text("#!/bin/bash\ncat <<'REPORT'\n" + payload + f"\nREPORT\nexit {status}\n")
    dashboard.chmod(0o755)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    (bin_dir / "git").write_text('#!/bin/bash\nprintf "%s\\n" "$TEST_ROOT"\n')
    (bin_dir / "gh").write_text(
        '#!/bin/bash\nprintf "%s\\n" "$*" >> "$TEST_ROOT/gh-calls"\n'
        'case "$*" in "auth status"|"issue list "*) exit 0;; *) exit 97;; esac\n'
    )
    for path in bin_dir.iterdir():
        path.chmod(0o755)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(PATH=str(bin_dir) + os.pathsep + env["PATH"], TEST_ROOT=str(tmp_path), DRY_RUN="true")
    result = subprocess.run(["bash", str(scripts / "compliance-cron.sh")],
                            env=env, capture_output=True, text=True, cwd=tmp_path, check=False)
    calls = (tmp_path / "gh-calls").read_text() if (tmp_path / "gh-calls").exists() else ""
    assert all(line == "auth status" or line.startswith("issue list ") for line in calls.splitlines())
    return result, (tmp_path / "logs/compliance").glob("*.log")


@pytest.mark.parametrize("reviewed,unreviewed,level", [(0, 1, "critical"), (1, 2, "high"), (3, 2, "medium")])
def test_cron_alert_severity(tmp_path, reviewed, unreviewed, level):
    """Issue threshold table: 0% critical, floor(100/3)=33% high, 300/5=60% medium."""
    result, logs = run_cron(tmp_path, output(report(reviewed, unreviewed)))
    assert result.returncode == 0
    assert f"severity: {level}" in result.stdout
    text = next(logs).read_text()
    assert "**Dashboard verdict:** FAIL\n" in text
    assert "FAIL\npass" not in text


@pytest.mark.parametrize("payload", [report(0, 0, 6), report(0, 0, 0), report(4, 1)])
def test_no_alert_for_pass_or_no_reviewable(tmp_path, payload):
    result, _ = run_cron(tmp_path, output(payload), status=0)
    assert result.returncode == 0
    assert "ALERT:" not in result.stdout
    assert "[DRY RUN]" not in result.stdout


@pytest.mark.parametrize("payload,status", [("broken", 2), (output(report()), 2), (output(report()), 0)])
def test_dashboard_failure_is_visible(tmp_path, payload, status):
    result, _ = run_cron(tmp_path, payload, status)
    assert result.returncode != 0
    assert "ERROR:" in result.stdout
    assert "ALERT:" not in result.stdout


@pytest.mark.parametrize("rate,level", [(29, "critical"), (30, "high"), (49, "high"),
                                       (50, "medium"), (79, "medium"), (80, None)])
def test_threshold_boundaries(tmp_path, rate, level):
    """Issue threshold table; with 100 reviewable commits, rate equals reviewed."""
    payload = report(rate, 100 - rate, 0)
    result, _ = run_cron(tmp_path, output(payload), status=0 if rate >= 80 else 1)
    assert result.returncode == 0
    if level:
        assert f"severity: {level}" in result.stdout
    else:
        assert "ALERT:" not in result.stdout
