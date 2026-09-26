"""Both legal gate workflows must also run on a clock.

Board commits pushed by kanban-reconcile use the default GITHUB_TOKEN, and
GitHub creates no workflow run for events that token raises. A `push` trigger
is therefore structurally blind to that writer; only `schedule:` can see what
it lands on main. The scheduled runs must be read-only: no write permission,
no persisted credential, no git write command.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
PII = WORKFLOWS / "legal-client-pii-gate.yml"
IDENTIFIER = WORKFLOWS / "legal-identifier-gate.yml"
BOTH = [PII, IDENTIFIER]


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _triggers(doc: dict) -> dict:
    # PyYAML (YAML 1.1) reads the bare key `on` as boolean True.
    trig = doc.get("on", doc.get(True))
    assert isinstance(trig, dict), trig
    return trig


@pytest.mark.parametrize("path", BOTH, ids=lambda p: p.name)
def test_workflow_has_a_daily_schedule(path):
    trig = _triggers(_load(path))
    crons = [entry.get("cron", "") for entry in trig.get("schedule") or []]
    assert crons, f"{path.name}: no schedule trigger"
    for cron in crons:
        fields = cron.split()
        assert len(fields) == 5, cron
        # At least daily: the day-of-month, month and day-of-week fields are wildcards.
        assert fields[2:] == ["*", "*", "*"], cron


@pytest.mark.parametrize("path", BOTH, ids=lambda p: p.name)
def test_workflow_keeps_its_pull_request_trigger_and_manual_dispatch(path):
    trig = _triggers(_load(path))
    assert "pull_request" in trig
    assert "workflow_dispatch" in trig


@pytest.mark.parametrize("path", BOTH, ids=lambda p: p.name)
def test_workflow_is_read_only(path):
    doc = _load(path)
    assert doc.get("permissions") == {"contents": "read"}, doc.get("permissions")
    for name, job in doc["jobs"].items():
        perms = job.get("permissions")
        if perms is not None:
            assert all(v in ("read", "none") for v in perms.values()), (name, perms)
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"\bgit\s+(push|commit|tag)\b", text), "git write command in a gate"
    assert not re.search(r"\bgh\s+(issue|pr|label|api)\b", text), "outward write surface in a gate"


def _job_by_name(doc: dict, display: str) -> dict:
    for job in doc["jobs"].values():
        if job.get("name") == display:
            return job
    raise AssertionError(f"no job named {display!r}")


def test_pii_pr_job_keeps_its_name_and_never_skips_on_a_pull_request():
    job = _job_by_name(_load(PII), "Client-PII Gate")
    cond = job.get("if", "")
    assert cond.replace(" ", "") == "github.event_name=='pull_request'", cond


def test_pii_gate_has_a_non_pr_whole_tree_job():
    doc = _load(PII)
    tree_jobs = [
        job for job in doc["jobs"].values()
        if job.get("if", "").replace(" ", "") == "github.event_name!='pull_request'"
    ]
    assert len(tree_jobs) == 1, "expected exactly one non-PR job"
    job = tree_jobs[0]
    runs = "\n".join(step.get("run", "") for step in job["steps"])
    assert "check-client-pii.py" in runs and "--all" in runs, runs
    assert "--base-ref" not in runs, "a scheduled run has no base ref"
    checkout = [s for s in job["steps"] if str(s.get("uses", "")).startswith("actions/checkout")]
    assert checkout and checkout[0].get("with", {}).get("persist-credentials") is False


def test_identifier_gate_checkout_persists_no_credential():
    doc = _load(IDENTIFIER)
    for job in doc["jobs"].values():
        for step in job["steps"]:
            if str(step.get("uses", "")).startswith("actions/checkout"):
                assert step.get("with", {}).get("persist-credentials") is False
