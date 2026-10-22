"""Alert regressions with synthetic reports; expected rates are hand calculations."""

from __future__ import annotations

import importlib.util
import json
import os
import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts/enforcement"
SPEC = importlib.util.spec_from_file_location(
    "compliance_alert", SCRIPTS / "compliance_alert.py"
)


def parser():
    module = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(module)
    return module.parse_report


def report(reviewed=0, unreviewed=0, skipped=7, threshold=80):
    """Source: dashboard guide, 'How Compliance is Calculated', steps 4–5.

    Reviewable = reviewed + unreviewed; percentage = floor(100 * reviewed /
    reviewable). With no reviewable commits the stored legacy rate is zero.
    The default threshold is the policy in the issue's Thresholds table.
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
        "stage_prompt_drift": {
            "counts": {"pass": 0},
            "latest_event": {"verdict": "pass", "reviewed": 999},
        },
    }


def output(payload):
    return "Compliance rate:    99%\nJSON Report:\n" + json.dumps(payload) + (
        "\n\nReport saved to: report.json\n"
    )


def test_nested_metrics_and_human_summary_are_not_commit_metrics():
    payload = report(reviewed=1, unreviewed=3)
    parsed = parser()(output(payload))
    # Independent calculation: 1 reviewed / (1 + 3) reviewable * 100 = 25%.
    assert parsed["compliance_rate"] == 25
    assert parsed["reviewed"] == 1
    assert parsed["verdict"] == "FAIL"


@pytest.mark.parametrize("field,value", [
    ("reviewed", -1), ("unreviewed", True), ("total_commits", "7"),
    ("reviewable", 1), ("compliance_rate", 100), ("threshold", 101),
    ("verdict", "FAIL"), ("skipped", 6),
])
def test_inconsistent_or_invalid_report_is_rejected(field, value):
    payload = report()
    payload[field] = value
    with pytest.raises(ValueError):
        parser()(output(payload))


@pytest.mark.parametrize("text", [
    "", "Compliance rate: 0%", 'JSON Report:\n{"total_commits": 0}',
    "JSON Report:\nnull", "JSON Report:\n[]",
    'JSON Report:\n{"verdict":"PASS","verdict":"FAIL"}',
    "JSON Report:\n{broken", "JSON Report:\n{}\nJSON Report:\n{}",
])
def test_missing_malformed_or_ambiguous_report_is_rejected(text):
    with pytest.raises(ValueError):
        parser()(text)


def run_cron(tmp_path, payload, status=0, *, real_dashboard=False):
    """Run only copied scripts in a disposable repository, with no remote access."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(["git", "init", str(tmp_path)], env=env, check=True,
                   capture_output=True)
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    for name in ("compliance-cron.sh", "compliance_alert.py"):
        shutil.copyfile(SCRIPTS / name, scripts / name)
    text = payload if isinstance(payload, str) else output(payload)
    dashboard = scripts / "compliance-dashboard.sh"
    dashboard.write_text(
        "#!/usr/bin/env bash\nprintf '%s' " + shlex.quote(text)
        + f"\nexit {status}\n", encoding="utf-8",
    )
    if real_dashboard:
        shutil.copyfile(SCRIPTS / "compliance-dashboard.sh", dashboard)
    dashboard.chmod(0o755)
    tools = tmp_path / "bin"
    tools.mkdir()
    gh = tools / "gh"
    gh.write_text(
        '#!/usr/bin/env bash\nprintf "%s\\n" "$*" >> "$GH_CALLS"\n'
        'if [[ "$1 $2" == "issue list" ]]; then echo null; fi\n',
        encoding="utf-8",
    )
    gh.chmod(0o755)
    calls = tmp_path / "gh-calls"
    env.update(DRY_RUN="true", PATH=str(tools) + os.pathsep + env["PATH"],
               GH_CALLS=str(calls))
    result = subprocess.run(["bash", str(scripts / "compliance-cron.sh")],
                            cwd=tmp_path.parent, env=env, capture_output=True, text=True, check=False)
    logs = "\n".join(p.read_text() for p in (tmp_path / "logs").rglob("*.log"))
    remote_calls = calls.read_text() if calls.exists() else ""
    assert not any(operation in remote_calls for operation in (
        "issue create", "issue comment", "issue edit", "label create",
    ))
    return result, logs, remote_calls


@pytest.mark.parametrize("skipped", [0, 7])
def test_no_reviewable_commits_do_not_alert(tmp_path, skipped):
    """0 / 0 has no defined percentage; zero review obligations means no alert."""
    result, logs, calls = run_cron(tmp_path, report(skipped=skipped))
    assert result.returncode == 0
    assert "No reviewable commits" in logs
    assert "ALERT:" not in logs
    assert calls == ""


@pytest.mark.parametrize("reviewed,unreviewed,severity", [
    (0, 7, "critical"), (29, 71, "critical"), (30, 70, "high"),
    (49, 51, "high"), (50, 50, "medium"), (79, 21, "medium"),
    (80, 20, None), (100, 0, None),
])
def test_alert_boundaries_and_exact_top_level_details(
    tmp_path, reviewed, unreviewed, severity,
):
    """Issue Thresholds table: <30, <50, <80; inputs sum to 100 except 0/7.

    Thus rates equal reviewed for each boundary; 0/7 * 100 = 0 for the
    critical reproduction. Expected values do not call the report parser.
    """
    payload = report(reviewed, unreviewed, skipped=0)
    result, logs, _ = run_cron(tmp_path, payload,
                               status=1 if severity else 0)
    assert result.returncode == 0
    if severity:
        assert f"severity: {severity}" in logs
        assert f"**Reviewed:** {reviewed} | **Unreviewed:** {unreviewed}" in logs
        assert "**Dashboard verdict:** FAIL\n" in logs
        assert "FAIL\npass" not in logs
    else:
        assert "PASS: Compliance" in logs
        assert "ALERT:" not in logs


@pytest.mark.parametrize("payload,status", [
    ("dashboard crashed", 2), ("Compliance rate: 0%", 0),
    (report(), 1), (report(0, 7), 0), (report(), 2),
])
def test_failed_or_inconsistent_execution_is_not_reported_as_compliance(
    tmp_path, payload, status,
):
    result, logs, calls = run_cron(tmp_path, payload, status)
    assert result.returncode != 0
    assert "ERROR:" in logs
    assert "ALERT:" not in logs
    assert calls == ""


def test_real_dashboard_empty_repository_contract(tmp_path):
    result, logs, calls = run_cron(tmp_path, "", real_dashboard=True)
    assert result.returncode == 0
    assert "No reviewable commits" in logs
    assert calls == ""
    assert len(list((tmp_path / "logs/compliance").glob("compliance-*.json"))) == 1


@pytest.mark.parametrize("reviewed,unreviewed,threshold,status,verdict", [
    (85, 15, 90, 1, "FAIL"), (60, 40, 50, 0, "PASS"),
])
def test_configured_threshold_preserves_alert_bands(
    tmp_path, reviewed, unreviewed, threshold, status, verdict,
):
    """Hand calculation: rates 85/100 and 60/100 yield 85% and 60%.

    A 90% dashboard criterion fails 85%; the issue's 80% alert criterion
    still alerts on 60% even when the configured dashboard criterion is 50%.
    These custom thresholds are synthetic inputs, not new policy constants.
    """
    result, logs, _ = run_cron(
        tmp_path, report(reviewed, unreviewed, threshold=threshold), status,
    )
    assert result.returncode == 0
    assert "severity: medium" in logs
    assert f"**Dashboard verdict:** {verdict}\n" in logs
