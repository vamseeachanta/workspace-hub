"""The `dispatch-pull` scheduled task and its wrapper (docs/runbooks/dispatch-pull.md).

Two properties are worth a test rather than a comment, because both fail
silently if they regress:

  * the task is registered under the SINGLETON runtime contract, and its cadence
    exceeds the loop's own arithmetic worst case — a tick that can meet its
    predecessor is the overlap bug the contract exists to refuse;
  * the wrapper never sets `DISPATCH_APPLY_ENABLED` itself. dispatch_pull's two
    gates only stay two gates while the second one comes from outside the repo.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[2]
SCHEDULE_PATH = REPO / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
WRAPPER_PATH = REPO / "scripts" / "cron" / "dispatch-pull-cron.sh"
RUNBOOK_PATH = REPO / "docs" / "runbooks" / "dispatch-pull.md"

#: dispatch_pull.DEFAULT_MAX_CARDS x drain.DEFAULT_TIMEOUT_SECONDS, plus the
#: gaps dispatch_pull.DEFAULT_DELAY_S puts between hand-offs. Restated here so a
#: change to any of the three shows up as a failing cadence assertion instead of
#: a schedule that quietly starts overlapping itself.
WORST_CASE_SECONDS = 5 * 3600 + 4 * 30


def _task(task_id: str) -> dict:
    catalog = yaml.safe_load(SCHEDULE_PATH.read_text(encoding="utf-8"))
    return next(item for item in catalog["tasks"] if item["id"] == task_id)


def test_dispatch_pull_task_is_registered_for_the_control_plane_box():
    task = _task("dispatch-pull")
    assert task["machines"] == ["dev-primary", "ace-linux-1"]
    assert task["roles"] == ["control-plane"]
    assert "scripts/cron/dispatch-pull-cron.sh" in task["command"]
    assert task["log"] == "logs/dispatch-pull/cron-*.log"


def test_dispatch_pull_declares_the_singleton_runtime_contract():
    runtime = _task("dispatch-pull")["runtime"]
    assert runtime["singleton"] is True
    assert runtime["state_dir"] == ".claude/state/cron-runtime/dispatch-pull"
    # The health threshold has to sit ABOVE the worst case, or a legitimate long
    # run reports `excessive_runtime` and the alarm stops meaning anything.
    assert runtime["max_seconds"] > WORST_CASE_SECONDS


def test_dispatch_pull_cadence_cannot_normally_meet_its_predecessor():
    schedule = _task("dispatch-pull")["schedule"]
    minute, hour, *rest = schedule.split()
    assert rest == ["*", "*", "*"]
    assert hour.startswith("*/")
    period_seconds = int(hour[2:]) * 3600
    assert period_seconds > WORST_CASE_SECONDS
    # Off the crowded minutes: */5 git-lock-reaper, */30 return-to-main-guard and
    # the 4-hourly repository-sync all land on :00.
    assert int(minute) not in (0, 5, 11, 17, 30, 47, 50)


def test_wrapper_delegates_through_the_singleton_runtime():
    wrapper = WRAPPER_PATH.read_text(encoding="utf-8")
    assert "cron_runtime.py" in wrapper
    assert "--task-id dispatch-pull" in wrapper
    assert "scripts/operations/dispatch_pull.py" in wrapper


def test_wrapper_never_arms_the_second_gate_itself():
    wrapper = WRAPPER_PATH.read_text(encoding="utf-8")
    code = [line for line in wrapper.splitlines() if not line.lstrip().startswith("#")]
    # Re-exporting an inherited value is the pass-through the loop needs; an
    # assignment would be this wrapper deciding drain may write. Anchored, so the
    # refusal message that NAMES the variable is not mistaken for setting it.
    assignment = re.compile(r"^\s*(?:export\s+)?DISPATCH_APPLY_ENABLED=")
    assert not any(assignment.search(line) for line in code)
    assert any(line.strip() == "export DISPATCH_APPLY_ENABLED" for line in code)
    # ...and --apply comes from its OWN variable, so one setting cannot arm both.
    assert "DISPATCH_PULL_APPLY" in wrapper


def test_runbook_exists_and_names_both_gates():
    text = RUNBOOK_PATH.read_text(encoding="utf-8")
    assert "--apply" in text
    assert "DISPATCH_APPLY_ENABLED=1" in text
    assert ".claude/dispatch/PAUSE" in text
    assert "run.sh cancel --job-id" in text
