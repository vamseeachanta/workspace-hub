"""Typed alert regression cases; policy source: issue #3596, Thresholds (2026)."""

import copy
import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts/enforcement/compliance_alert.py"


@pytest.fixture
def alert_module():
    spec = importlib.util.spec_from_file_location("compliance_alert", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(autouse=True)
def isolated_git_environment(monkeypatch):
    """Fixture repositories must not inherit bindings to the caller's checkout."""
    for variable in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        monkeypatch.delenv(variable, raising=False)


def report(reviewed=3, unreviewed=13, skipped=33, threshold=80):
    """Independent calculation: 49 - 33 = 16; floor(3 * 100 / 16) = 18.

    These counts reproduce issue #3596 (2026) without copying commit subjects.
    The percentage conversion and denominator follow the dashboard guide.
    """
    reviewable = reviewed + unreviewed
    rate = reviewed * 100 // reviewable if reviewable else 0
    return {
        "schema_version": 1,
        "timestamp": "2026-07-23T06:00:00+00:00",
        "window_hours": 24,
        "total_commits": reviewable + skipped,
        "reviewable": reviewable,
        "skipped": skipped,
        "reviewed": reviewed,
        "unreviewed": unreviewed,
        "compliance_rate": rate,
        "threshold": threshold,
        "verdict": "FAIL" if reviewable and rate < threshold else "PASS",
        "unreviewed_commits": [
            {"hash": f"{i:040x}", "subject": f"fix(core): change {i}"}
            for i in range(unreviewed)
        ],
        "stage_prompt_drift": {"latest_event": {"verdict": "pass"}},
    }


def build(module, payload):
    return module.build_alert(payload, "2026-07-23", "2026-W30")


def test_worked_example_uses_top_level_verdict(alert_module):
    result = build(alert_module, report())
    assert result["rate"] == 18
    assert result["severity"] == "critical"
    assert "**Dashboard verdict:** FAIL\n" in result["body"]
    assert "FAIL\npass" not in result["body"]
    assert "**Reviewable:** 16" in result["body"]
    assert f"{report()['unreviewed_commits'][0]['hash']} fix(core): change 0" in result["body"]
    assert "NOT_EVALUATED" in result["body"]


@pytest.mark.parametrize("skipped", [0, 4])
def test_no_reviewable_commits_do_not_alert(alert_module, skipped):
    """Both 0/0 and all-skipped windows have no review obligations."""
    result = build(alert_module, report(0, 0, skipped))
    assert result["action"] == "no-alert"
    assert result["reason"] == "no-reviewable-commits"


@pytest.mark.parametrize(
    ("rate", "severity"),
    [(0, "critical"), (29, "critical"), (30, "high"), (49, "high"),
     (50, "medium"), (79, "medium"), (80, None), (100, None)],
)
def test_threshold_boundaries(alert_module, rate, severity):
    """With 100 obligations the percentage equals the reviewed count.

    Boundary expectations come from issue #3596 (2026), Thresholds table.
    """
    result = build(alert_module, report(rate, 100 - rate))
    assert result.get("severity") == severity
    assert result["action"] == ("alert" if severity else "no-alert")


def test_configured_dashboard_threshold_is_used(alert_module):
    assert build(alert_module, report(85, 15, threshold=90))["severity"] == "medium"


@pytest.mark.parametrize(
    ("key", "value"),
    [("total_commits", 50), ("reviewable", 17), ("reviewed", -1),
     ("unreviewed", True), ("compliance_rate", 19), ("threshold", 101),
     ("verdict", "PASS"), ("schema_version", 2), ("window_hours", 0),
     ("timestamp", "2026-07-22T06:00:00Z"), ("timestamp", "invalid"),
     ("timestamp", "2026-07-23T06:00:00"), ("unreviewed_commits", [])],
)
def test_invalid_report_is_rejected(alert_module, key, value):
    payload = report()
    payload[key] = value
    with pytest.raises(ValueError):
        build(alert_module, payload)


def test_missing_field_is_rejected(alert_module):
    payload = report()
    del payload["reviewable"]
    with pytest.raises(ValueError):
        build(alert_module, payload)


@pytest.mark.parametrize("field", ["hash", "subject"])
def test_invalid_backlog_entry_is_rejected(alert_module, field):
    payload = report()
    payload["unreviewed_commits"][0][field] = "invalid\ntext"
    with pytest.raises(ValueError):
        build(alert_module, payload)


@pytest.mark.parametrize("codepoint", [*range(9), *range(10, 32), 127])
def test_backlog_subject_rejects_other_control_characters(alert_module, codepoint):
    payload = report()
    payload["unreviewed_commits"][0]["subject"] = f"fix(core): before{chr(codepoint)}after"
    with pytest.raises(ValueError, match="invalid backlog subject"):
        build(alert_module, payload)


def test_duplicate_backlog_hash_is_rejected(alert_module):
    payload = report()
    payload["unreviewed_commits"][1] = copy.deepcopy(payload["unreviewed_commits"][0])
    with pytest.raises(ValueError):
        build(alert_module, payload)


def test_commit_subject_cannot_close_markdown_fence(alert_module):
    payload = report()
    payload["unreviewed_commits"][0]["subject"] = "fix(core): ``` quoted"
    body = build(alert_module, payload)["body"]
    assert f"    {payload['unreviewed_commits'][0]['hash']} fix(core): ``` quoted" in body
    assert not any(line.startswith("```") for line in body.splitlines())


@pytest.fixture
def cron(tmp_path):
    """Run a copied wrapper with fake Git, dashboard and publication commands."""
    scripts = tmp_path / "scripts/enforcement"
    scripts.mkdir(parents=True)
    for name in ("compliance-cron.sh", "compliance_alert.py"):
        source = ROOT / "scripts/enforcement" / name
        if source.exists():
            shutil.copyfile(source, scripts / name)
    dashboard = scripts / "compliance-dashboard.sh"
    dashboard.write_text(
        '#!/bin/sh\ncat "$TEST_REPORT"\nexit "$TEST_DASHBOARD_EXIT"\n',
        encoding="utf-8", newline="\n",
    )
    dashboard.chmod(0o755)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    git = bin_dir / "git"
    git.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$TEST_REPO"\n',
        encoding="utf-8", newline="\n",
    )
    git.chmod(0o755)
    date = bin_dir / "date"
    date.write_text(
        '#!/bin/sh\ncase "$1" in\n'
        ' +%Y%m%d) echo 20260723;;\n +%Y-%m-%d) echo 2026-07-23;;\n'
        ' +%G-W%V) echo 2026-W30;;\n +%V) echo 30;;\n +%Y) echo 2026;;\n'
        ' *) echo 2026-07-23T06:00:00+00:00;;\nesac\n',
        encoding="utf-8", newline="\n",
    )
    date.chmod(0o755)
    publisher = bin_dir / "gh"
    publisher.write_text(
        '#!/usr/bin/env python3\nimport json, os, sys\n'
        'with open(os.environ["TEST_CALLS"], "a", encoding="utf-8", newline="\\n") as out:\n'
        '    out.write(json.dumps(sys.argv[1:]) + "\\n")\n'
        'if sys.argv[1:3] == ["issue", os.environ.get("TEST_FAIL", "")]:\n'
        '    raise SystemExit(1)\n'
        'if sys.argv[1:3] == ["issue", "list"]:\n'
        '    print(os.environ.get("TEST_EXISTING", ""))\n',
        encoding="utf-8", newline="\n",
    )
    publisher.chmod(0o755)
    payload = tmp_path / "input.json"
    calls = tmp_path / "calls.jsonl"
    env = {
        **os.environ, "HOME": str(tmp_path), "PATH": f"{bin_dir}:{os.environ['PATH']}",
        "TEST_REPO": str(tmp_path), "TEST_REPORT": str(payload),
        "TEST_CALLS": str(calls), "TEST_DASHBOARD_EXIT": "1",
        "COMPLIANCE_REPORTS_DIR": str(tmp_path / "reports"),
    }

    def invoke(data=None, **overrides):
        payload.write_text(
            json.dumps(data if data is not None else report()),
            encoding="utf-8", newline="\n",
        )
        result = subprocess.run(
            ["bash", str(scripts / "compliance-cron.sh")], env={**env, **overrides},
            text=True, capture_output=True, check=False,
        )
        recorded = [json.loads(line) for line in calls.read_text(encoding="utf-8").splitlines()] if calls.exists() else []
        return result, recorded

    return invoke


def test_dry_run_never_calls_publisher(cron):
    result, calls = cron(DRY_RUN="true")
    assert result.returncode == 0
    assert "[DRY RUN]" in result.stdout
    assert calls == []


@pytest.mark.parametrize("skipped", [0, 4])
def test_cron_no_obligations_do_not_publish(cron, skipped):
    result, calls = cron(report(0, 0, skipped), TEST_DASHBOARD_EXIT="0")
    assert result.returncode == 0
    assert calls == []


@pytest.mark.parametrize("existing", ["", "42"])
def test_cron_create_or_update_uses_validated_body(cron, existing):
    result, calls = cron(TEST_EXISTING=existing)
    assert result.returncode == 0, result.stderr
    action = "comment" if existing else "create"
    published = next(call for call in calls if call[:2] == ["issue", action])
    body = published[published.index("--body") + 1]
    assert "**Dashboard verdict:** FAIL" in body
    assert "FAIL\npass" not in body
    if not existing:
        assert "compliance-alert-2026-W30" in body
    search = next(call for call in calls if call[:2] == ["issue", "list"])
    assert "compliance-alert-2026-W30" in search[search.index("--search") + 1]


@pytest.mark.parametrize("exit_code", ["0", "2"])
def test_cron_rejects_inconsistent_dashboard_status(cron, exit_code):
    result, calls = cron(TEST_DASHBOARD_EXIT=exit_code)
    assert result.returncode != 0
    assert calls == []


def test_cron_rejects_invalid_counts_without_publishing(cron):
    payload = report()
    payload["total_commits"] += 1
    result, calls = cron(payload)
    assert result.returncode != 0
    assert calls == []


@pytest.mark.parametrize("length", [39, 41, 63, 65])
def test_only_git_object_hash_lengths_are_accepted(alert_module, length):
    """Git 2.55.0, hash-function-transition, Object names: 40 or 64 hex digits.

    Source: https://git-scm.com/docs/hash-function-transition (2026-10-22).
    """
    payload = report()
    payload["unreviewed_commits"][0]["hash"] = "f" * length
    with pytest.raises(ValueError):
        build(alert_module, payload)


@pytest.mark.parametrize("day", ["2027-01-01", "2027-01-03"])
def test_iso_year_is_used_at_calendar_boundary(alert_module, day):
    """ISO calendar: Friday Jan 1 and Sunday Jan 3 belong to 2026-W53.

    Independent calendar counting: 2026 starts on Thursday; the week containing
    Thursday Dec 31 ends on Sunday Jan 3, before the first Thursday of 2027.
    """
    payload = report()
    payload["timestamp"] = f"{day}T06:00:00+00:00"
    alert = alert_module.build_alert(payload, day, "2026-W53")
    assert alert["dedup_key"] == "compliance-alert-2026-W53"
    with pytest.raises(ValueError):
        alert_module.build_alert(payload, day, "2027-W53")


@pytest.mark.parametrize("raw", ['{"total_commits":', "null", "[]"])
def test_cli_rejects_malformed_documents(raw):
    result = subprocess.run(
        ["python3", str(MODULE), "--date", "2026-07-23", "--week", "2026-W30"],
        input=raw, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 2
    assert not result.stdout
    assert "ERROR: Invalid compliance report:" in result.stderr


@pytest.mark.parametrize("command", ["list", "create", "comment"])
def test_publisher_failure_is_not_reported_as_success(cron, command):
    result, calls = cron(TEST_FAIL=command, TEST_EXISTING="42" if command == "comment" else "")
    assert result.returncode != 0
    if command == "list":
        assert not any(call[:2] == ["issue", "create"] for call in calls)


@pytest.mark.parametrize("separator", [" ", "\t", "\u2028", "\u2029", "\u0085"])
def test_actual_dashboard_to_cron_dry_run(tmp_path, separator):
    """One unreviewed change gives floor(0 * 100 / 1) = 0, a critical alert.

    The nested drift verdict is pass but the compliance verdict remains FAIL.
    Threshold source: issue #3596, Thresholds (2026).
    """
    from test_compliance_dashboard import init_repo, run

    init_repo(tmp_path)
    scripts = tmp_path / "scripts/enforcement"
    scripts.mkdir(parents=True)
    for name in ("compliance-cron.sh", "compliance-dashboard.sh", "compliance_alert.py"):
        shutil.copyfile(ROOT / "scripts/enforcement" / name, scripts / name)
    (scripts / "compliance-dashboard.sh").chmod(0o755)
    subject = f"fix(core): before{separator}after"
    run(["git", "commit", "--allow-empty", "-m", subject], tmp_path)
    logs = tmp_path / "logs/hooks"
    logs.mkdir(parents=True)
    (logs / "stage-prompt-drift-events.jsonl").write_text(
        '{"verdict":"pass"}\n', encoding="utf-8", newline="\n",
    )
    output_dir = tmp_path / "reports"
    result = subprocess.run(
        ["bash", str(scripts / "compliance-cron.sh")], cwd=tmp_path,
        env={**os.environ, "DRY_RUN": "true", "COMPLIANCE_REPORTS_DIR": str(output_dir)},
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    log = next(output_dir.glob("daily-*.log")).read_text(encoding="utf-8")
    assert "**Dashboard verdict:** FAIL\n" in log
    assert "**Severity:** critical" in log
    assert subject in log
    saved = json.loads(next(output_dir.glob("compliance-*.json")).read_text(encoding="utf-8"))
    assert saved["unreviewed_commits"][0]["subject"] == subject
    assert "FAIL\npass" not in log
    assert "[DRY RUN]" in result.stdout


def test_cli_rejects_duplicate_json_fields():
    payload = json.dumps(report())
    raw = '{"verdict":"PASS",' + payload[1:]
    result = subprocess.run(
        ["python3", str(MODULE), "--date", "2026-07-23", "--week", "2026-W30"],
        input=raw, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 2
    assert not result.stdout
