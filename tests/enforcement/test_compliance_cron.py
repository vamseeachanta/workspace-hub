"""Alert regressions based on issue 3940 (2026), Thresholds and empty samples.

All counts below are synthetic inputs. Expected percentages are independent
hand calculations: reviewable = total - skipped; rate = floor(100 * reviewed /
reviewable). The severity limits come from that issue's Thresholds table.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2] / "scripts" / "enforcement"


def report(total=1, skipped=0, reviewed=0, threshold=80):
    """Synthetic count partition; percentage definition is in the module docstring."""
    reviewable = total - skipped
    rate = reviewed * 100 // reviewable if reviewable else 0
    return {
        "total_commits": total,
        "skipped": skipped,
        "reviewable": reviewable,
        "reviewed": reviewed,
        "unreviewed": reviewable - reviewed,
        "compliance_rate": rate,
        "threshold": threshold,
        "verdict": "FAIL" if reviewable and rate < threshold else "PASS",
        "stage_prompt_drift": {"counts": {"pass": 1}, "verdict": "pass"},
    }


@pytest.fixture
def workspace(tmp_path):
    """Run the shipped wrapper in isolation, with no real GitHub operations."""
    scripts = tmp_path / "scripts" / "enforcement"
    scripts.mkdir(parents=True)
    for name in ("compliance-cron.sh", "compliance-dashboard.sh", "compliance-alert.py"):
        if (SOURCE / name).exists():
            shutil.copy2(SOURCE / name, scripts / name)
    tools = tmp_path / "bin"
    tools.mkdir()
    (tools / "git").write_text(
        '#!/usr/bin/env bash\n'
        'if [[ "$*" == *rev-parse* ]]; then\n'
        '  printf "%s\\n" "$FIXTURE_ROOT"\n'
        'elif [[ "$*" == *--since=* ]]; then\n'
        '  printf "%s" "${FIXTURE_COMMITS:-}"\n'
        'else\n'
        '  printf "%s" "${FIXTURE_EVIDENCE:-}"\n'
        'fi\n'
    )
    (tools / "gh").write_text(
        '#!/usr/bin/env bash\n'
        'printf "%s\\n" "$*" >> "$FIXTURE_ROOT/gh-calls"\n'
        'if [[ "$1 $2" == "issue list" ]]; then\n'
        '  printf "%s" "${FIXTURE_EXISTING:-}"\n'
        'fi\n'
    )
    for tool in tools.iterdir():
        tool.chmod(0o755)
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(
        PATH=f"{tools}{os.pathsep}{os.environ['PATH']}",
        FIXTURE_ROOT=str(tmp_path),
        DRY_RUN="true",
        COMPLIANCE_THRESHOLD="80",
        COMPLIANCE_WINDOW_HOURS="24",
    )
    return tmp_path, scripts, env


def invoke(workspace, payload=None, *, status=None, raw=None, dry_run=True):
    root, scripts, env = workspace
    if payload is not None or raw is not None:
        (scripts / "compliance-dashboard.sh").write_text(
            '#!/usr/bin/env bash\nprintf "%s\\n" "$FIXTURE_OUTPUT"\n'
            'exit "$FIXTURE_STATUS"\n'
        )
        (scripts / "compliance-dashboard.sh").chmod(0o755)
        env["FIXTURE_OUTPUT"] = raw if raw is not None else (
            "JSON Report:\n" + json.dumps(payload) + "\n\nReport saved to: ignored"
        )
        env["FIXTURE_STATUS"] = str(
            status if status is not None else int(payload["verdict"] == "FAIL")
        )
    env["DRY_RUN"] = str(dry_run).lower()
    result = subprocess.run(
        ["bash", str(scripts / "compliance-cron.sh")],
        cwd=root, env=env, capture_output=True, text=True, check=False,
    )
    logs = "\n".join(path.read_text() for path in (root / "logs/compliance").glob("*.log"))
    calls = (root / "gh-calls").read_text() if (root / "gh-calls").exists() else ""
    return result, logs, calls


@pytest.mark.parametrize("total,skipped", [(0, 0), (1, 1), (4, 4)])
def test_empty_reviewable_sample_never_alerts(workspace, total, skipped):
    """Issue 3940: total - skipped = 0; division is undefined, not a violation."""
    result, _, calls = invoke(workspace, report(total, skipped), dry_run=False)
    assert result.returncode == 0
    assert "No reviewable commits" in result.stdout
    assert "ALERT:" not in result.stdout
    assert not calls


@pytest.mark.parametrize(
    "reviewed,severity",
    [(0, "critical"), (29, "critical"), (30, "high"), (49, "high"),
     (50, "medium"), (79, "medium"), (80, None), (100, None)],
)
def test_sourced_threshold_boundaries(workspace, reviewed, severity):
    """Issue 3940 table: with 100 reviewable, 100 * reviewed / 100 = reviewed %."""
    result, logs, calls = invoke(workspace, report(100, reviewed=reviewed))
    assert result.returncode == 0
    assert not calls, "A dry run must not call GitHub, even for authentication"
    if severity:
        assert f"severity: {severity}" in result.stdout
        assert f"**Unreviewed:** {100 - reviewed}" in logs
        assert "**Dashboard verdict:** FAIL\n" in logs
        assert "FAIL\npass" not in logs
    else:
        assert "PASS:" in result.stdout
        assert "ALERT:" not in result.stdout


def test_fractional_rate_uses_dashboard_integer_arithmetic(workspace):
    """Hand calculation: total 4 - skipped 1 = 3; floor(100 * 2 / 3) = 66%."""
    result, logs, _ = invoke(workspace, report(4, skipped=1, reviewed=2))
    assert result.returncode == 0
    assert "Compliance rate: 66%" in result.stdout
    assert "severity: medium" in result.stdout
    assert "**Total commits:** 4 | **Reviewed:** 2 | **Unreviewed:** 1" in logs


def test_custom_dashboard_threshold_keeps_alert_policy(workspace):
    """Issue 3940 alert table still makes 50 / 100 medium at dashboard limit 40."""
    result, logs, _ = invoke(workspace, report(100, reviewed=50, threshold=40))
    assert result.returncode == 0
    assert "severity: medium" in result.stdout
    assert "**Dashboard verdict:** PASS" in logs


@pytest.mark.parametrize(
    "change",
    [{"reviewable": 0}, {"reviewed": -1}, {"total_commits": True},
     {"unreviewed": "1"}, {"compliance_rate": 100}, {"verdict": "PASS"},
     {"threshold": 101}, {"skipped": 2}, {"reviewed": 1.0}],
)
def test_inconsistent_reports_fail_without_alerting(workspace, change):
    payload = report()
    payload.update(change)
    result, _, calls = invoke(workspace, payload, status=1, dry_run=False)
    assert result.returncode != 0
    assert "ERROR:" in result.stdout
    assert "ALERT:" not in result.stdout
    assert not calls


@pytest.mark.parametrize("raw", ["", "Compliance rate: 0%", "JSON Report:\n{}", "JSON Report:\n{"])
def test_missing_or_malformed_json_is_an_error(workspace, raw):
    result, _, calls = invoke(workspace, raw=raw, status=0, dry_run=False)
    assert result.returncode != 0
    assert "ERROR:" in result.stdout
    assert not calls


@pytest.mark.parametrize("mutation", ["array", "duplicate", "missing", "two-reports"])
def test_ambiguous_json_is_rejected(workspace, mutation):
    """A report must be one object with one unambiguous value per field."""
    payload = report()
    raw = json.dumps(payload)
    if mutation == "array":
        raw = "[]"
    elif mutation == "duplicate":
        raw = raw[:-1] + ', "reviewed": 1}'
    elif mutation == "missing":
        del payload["reviewed"]
        raw = json.dumps(payload)
    else:
        raw += "\nJSON Report:\n" + raw
    result, _, calls = invoke(
        workspace, raw="JSON Report:\n" + raw, status=1, dry_run=False,
    )
    assert result.returncode != 0
    assert not calls


@pytest.mark.parametrize("status", [0, 2])
def test_dashboard_failure_cannot_be_hidden_by_parseable_output(workspace, status):
    result, _, calls = invoke(workspace, report(), status=status, dry_run=False)
    assert result.returncode != 0
    assert not calls


@pytest.mark.parametrize("commits", ["", "a" * 40 + " docs(guide): update text\n"])
def test_real_dashboard_empty_sample_integration(workspace, commits):
    workspace[2]["FIXTURE_COMMITS"] = commits
    result, _, calls = invoke(workspace, dry_run=False)
    assert result.returncode == 0
    assert "No reviewable commits" in result.stdout
    assert not calls


def test_real_dashboard_genuine_violation_keeps_commit_details(workspace):
    workspace[2]["FIXTURE_COMMITS"] = "b" * 40 + " feat(core): implement cache\n"
    result, logs, calls = invoke(workspace)
    assert result.returncode == 0
    assert "severity: critical" in result.stdout
    assert "  - bbbbbbbb feat(core): implement cache" in logs
    assert not calls


def test_real_dashboard_compliant_sample_does_not_alert(workspace):
    """Hand calculation: one qualifying item with evidence gives 100 * 1 / 1 = 100%."""
    workspace[2]["FIXTURE_COMMITS"] = "c" * 40 + " feat(core): implement cache\n"
    workspace[2]["FIXTURE_EVIDENCE"] = "approved"
    result, _, calls = invoke(workspace, dry_run=False)
    assert result.returncode == 0
    assert "PASS: Compliance at 100%" in result.stdout
    assert not calls


def test_current_dashboard_output_cannot_fall_back_to_stale_report(workspace):
    """A prior valid file cannot mask this invocation's missing JSON."""
    log_dir = workspace[0] / "logs/compliance"
    log_dir.mkdir(parents=True)
    (log_dir / "compliance-old.json").write_text(json.dumps(report()))
    result, _, calls = invoke(workspace, raw="dashboard failed", status=2, dry_run=False)
    assert result.returncode != 0
    assert not calls


@pytest.mark.parametrize("existing", ["", "123"])
def test_valid_alert_reaches_mocked_create_or_update(workspace, existing):
    workspace[2]["FIXTURE_EXISTING"] = existing
    result, _, calls = invoke(workspace, report(), dry_run=False)
    assert result.returncode == 0
    assert "auth status" in calls
    assert ("issue comment 123" if existing else "issue create") in calls
