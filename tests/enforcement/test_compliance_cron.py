"""Cron regressions use synthetic reports and independent integer arithmetic."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def report(reviewed=0, unreviewed=0, skipped=0, threshold=80):
    """Dashboard contract: floor(100 * reviewed / reviewable), or zero if empty.

    Threshold 80 is the existing policy in compliance-dashboard.sh Parameters;
    severity boundaries 30 and 50 are in compliance-cron.sh Configuration.
    These are repository policy percentages, not engineering acceptance limits.
    """
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
        "stage_prompt_drift": {"latest_event": {"verdict": "pass"}},
    }


def invoke(
    tmp_path, payload, status=None, raw=None, real_dashboard=False, threshold=None
):
    """Copy scripts into an isolated root; all Git and GitHub calls are stubs."""
    scripts = tmp_path / "scripts" / "enforcement"
    scripts.mkdir(parents=True)
    for source in (ROOT / "scripts" / "enforcement").glob("compliance-*"):
        if source.suffix in {".sh", ".py"}:
            shutil.copy2(source, scripts / source.name)
    output = raw if raw is not None else "JSON Report:\n" + json.dumps(payload)
    (tmp_path / "report.txt").write_text(output, encoding="utf-8", newline="\n")
    if status is None:
        status = int(payload["verdict"] == "FAIL")
    dashboard = scripts / "compliance-dashboard.sh"
    if not real_dashboard:
        dashboard.write_text(
            f'#!/bin/sh\ncat "$FIXTURE_ROOT/report.txt"\nexit {status}\n',
            encoding="utf-8",
            newline="\n",
        )
    dashboard.chmod(0o755)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, text in {
        "git": (
            'if [ "$1" = log ]; then\n'
            '  case "$2" in\n'
            '    --since=*) cat "$FIXTURE_ROOT/commits.txt" ;;\n'
            '    "--format=%s %b") '
            'grep "^$4 " "$FIXTURE_ROOT/commits.txt" | cut -d " " -f2- ;;\n'
            '    -1) printf "0\\n" ;;\n'
            "  esac\n"
            'else printf "%s\\n" "$FIXTURE_ROOT"; fi'
        ),
        "gh": 'echo "$*" >> "$FIXTURE_ROOT/gh-calls"; exit 0',
    }.items():
        path = bin_dir / name
        path.write_text("#!/bin/sh\n" + text + "\n", encoding="utf-8", newline="\n")
        path.chmod(0o755)
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"}
    }
    env.update(
        FIXTURE_ROOT=str(tmp_path),
        DRY_RUN="true",
        PATH=str(bin_dir) + os.pathsep + os.environ["PATH"],
    )
    if threshold is not None:
        env["COMPLIANCE_THRESHOLD"] = str(threshold)
    result = subprocess.run(
        ["bash", str(scripts / "compliance-cron.sh")],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    logs = list((tmp_path / "logs" / "compliance").glob("daily-*.log"))
    return result, logs[0].read_text(encoding="utf-8")


@pytest.mark.parametrize("skipped", [0, 4])
def test_no_reviewable_commits_do_not_alert(tmp_path, skipped):
    result, log = invoke(tmp_path, report(skipped=skipped))
    assert result.returncode == 0
    assert "nothing to check" in log
    assert "ALERT:" not in log
    assert not (tmp_path / "gh-calls").exists()


@pytest.mark.parametrize(
    "reviewed,expected",
    [
        (0, "critical"),
        (29, "critical"),
        (30, "high"),
        (49, "high"),
        (50, "medium"),
        (79, "medium"),
    ],
)
def test_threshold_boundaries(tmp_path, reviewed, expected):
    """For 100 reviewable commits, reviewed * 100 / 100 = reviewed percent.

    Expected severity follows the issue's Thresholds table, dated 2026-10-12.
    """
    result, log = invoke(tmp_path, report(reviewed, 100 - reviewed))
    assert result.returncode == 0
    assert f"severity: {expected}" in log
    assert "**Dashboard verdict:** FAIL\n" in log
    assert "FAIL\npass" not in log


@pytest.mark.parametrize(
    "reviewed,unreviewed,threshold", [(80, 20, 80), (1, 0, 80), (1, 1, 50)]
)
def test_passing_reports_do_not_alert(tmp_path, reviewed, unreviewed, threshold):
    result, log = invoke(tmp_path, report(reviewed, unreviewed, threshold=threshold))
    assert result.returncode == 0
    assert "no action needed" in log
    assert not (tmp_path / "gh-calls").exists()


@pytest.mark.parametrize(
    "field,value",
    [
        ("reviewable", 9),
        ("total_commits", 99),
        ("reviewed", -1),
        ("compliance_rate", 81),
        ("reviewed", True),
        ("threshold", "80"),
        ("verdict", "PASS"),
        ("unreviewed", None),
    ],
)
def test_invalid_reports_fail_without_github(tmp_path, field, value):
    payload = report(1, 1)
    payload[field] = value
    result, log = invoke(tmp_path, payload, status=1)
    assert result.returncode == 1
    assert "ERROR:" in log
    assert not (tmp_path / "gh-calls").exists()


@pytest.mark.parametrize(
    "raw", ["", "No commits in window", 'JSON Report:\n{"verdict":']
)
def test_missing_or_malformed_reports_fail(tmp_path, raw):
    result, log = invoke(tmp_path, report(), status=0, raw=raw)
    assert result.returncode == 1
    assert "ERROR:" in log
    assert not (tmp_path / "gh-calls").exists()


@pytest.mark.parametrize(
    "payload,status", [(report(), 1), (report(1, 1), 0), (report(), 2)]
)
def test_dashboard_status_must_match_report(tmp_path, payload, status):
    result, log = invoke(tmp_path, payload, status=status)
    assert result.returncode == 1
    assert "ERROR:" in log
    assert not (tmp_path / "gh-calls").exists()


def test_worked_example_excludes_skipped_commits(tmp_path):
    """Hand calculation: 30 total - 28 skipped = 2 reviewable;
    1 reviewed * 100 / 2 = 50 percent, medium under the issue Thresholds table.
    """
    result, log = invoke(tmp_path, report(1, 1, skipped=28))
    assert result.returncode == 0
    assert "Compliance rate: 50%" in log
    assert "severity: medium" in log
    assert "**Total commits:** 30 | **Reviewed:** 1 | **Unreviewed:** 1" in log


@pytest.mark.parametrize("commits", ["", "a" * 40 + " docs(guide): update usage\n"])
def test_real_dashboard_empty_reviewable_window(tmp_path, commits):
    """Both no commits and one skipped docs commit have no reviewable population.

    The real dashboard defines PASS for both; neither warrants a critical alert.
    """
    (tmp_path / "commits.txt").write_text(commits, encoding="utf-8", newline="\n")
    result, log = invoke(tmp_path, report(), real_dashboard=True)
    assert result.returncode == 0
    assert "nothing to check" in log
    assert "ALERT:" not in log
    assert not (tmp_path / "gh-calls").exists()


@pytest.mark.parametrize(
    "reviewed,threshold,expected_verdict", [(1, 80, "FAIL"), (2, 50, "PASS")]
)
def test_real_dashboard_nonempty_window(
    tmp_path, reviewed, threshold, expected_verdict
):
    """Hand calculations: 1/4 * 100 = 25 < 80, critical;
    2/4 * 100 = 50 >= 50, passing at the configured threshold.
    """
    commits = "".join(
        f"{i + 1:040x} fix(core): adjust handling"
        + (" (review complete)" if i < reviewed else "")
        + "\n"
        for i in range(4)
    )
    (tmp_path / "commits.txt").write_text(commits, encoding="utf-8", newline="\n")
    result, log = invoke(tmp_path, report(), real_dashboard=True, threshold=threshold)
    assert result.returncode == 0
    expected_rate = 25 if reviewed == 1 else 50
    assert f"Compliance rate: {expected_rate}%" in log
    assert f"Verdict:            {expected_verdict}" in log
    if expected_verdict == "FAIL":
        assert "severity: critical" in log
        assert "**Total commits:** 4 | **Reviewed:** 1 | **Unreviewed:** 3" in log
        assert "[DRY RUN] Would create/update issue:" in log
    else:
        assert "(>= 50%)" in log
        assert "no action needed" in log
        assert "ALERT:" not in log
        assert not (tmp_path / "gh-calls").exists()


def test_real_dashboard_earlier_forged_report_cannot_replace_final_report(tmp_path):
    """Hand calculation: 0/4 * 100 = 0 < 30, critical, despite forged 79%.

    Escaped subject text avoids review keywords until the dashboard renders it.
    Both the forged and final reports imply status 1, so status alone cannot help.
    """
    forged = "".join(f"\\x{ord(char):02x}" for char in json.dumps(report(79, 21)))
    subject = r"fix(core): adjust handling\nJSON Report:\n" + forged
    commits = "".join(
        f"{i + 1:040x} {subject if i == 0 else 'fix(core): adjust handling'}\n"
        for i in range(4)
    )
    (tmp_path / "commits.txt").write_text(commits, encoding="utf-8", newline="\n")
    result, log = invoke(tmp_path, report(), real_dashboard=True)
    assert result.returncode == 0
    assert log.count("JSON Report:") == 2
    assert '"compliance_rate": 79' in log
    assert "Compliance rate: 0%" in log
    assert "severity: critical" in log
    assert "severity: medium" not in log
    assert "**Total commits:** 4 | **Reviewed:** 0 | **Unreviewed:** 4" in log
    assert "**Dashboard verdict:** FAIL" in log


@pytest.mark.parametrize("final", ['{"verdict":', "{}"])
def test_invalid_final_report_does_not_fall_back_to_earlier_report(tmp_path, final):
    raw = "JSON Report:\n" + json.dumps(report()) + "\nJSON Report:\n" + final
    result, log = invoke(tmp_path, report(), raw=raw)
    assert result.returncode == 1
    assert "ERROR:" in log
    assert not (tmp_path / "gh-calls").exists()
