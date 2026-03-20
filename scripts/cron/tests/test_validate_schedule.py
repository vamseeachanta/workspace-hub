"""Tests for schedule-tasks.yaml validator."""

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEDULE_FILE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"
VALIDATOR = REPO_ROOT / "scripts" / "cron" / "validate-schedule.py"

REQUIRED_TASK_FIELDS = {"id", "label", "schedule", "machines", "command", "description"}
VALID_SCHEDULERS = {"cron", "windows-task-scheduler"}
VALID_MACHINES = {
    "dev-primary",
    "dev-secondary",
    "licensed-win-1",
    "licensed-win-2",
    "gali-linux-compute-1",
}


@pytest.fixture(scope="module")
def schedule_data():
    assert SCHEDULE_FILE.exists(), f"{SCHEDULE_FILE} does not exist"
    with open(SCHEDULE_FILE) as f:
        data = yaml.safe_load(f)
    return data


@pytest.fixture(scope="module")
def tasks(schedule_data):
    return schedule_data.get("tasks", [])


def test_schedule_file_exists():
    assert SCHEDULE_FILE.exists()


def test_has_tasks_key(schedule_data):
    assert "tasks" in schedule_data
    assert isinstance(schedule_data["tasks"], list)
    assert len(schedule_data["tasks"]) > 0


def test_each_task_has_required_fields(tasks):
    for task in tasks:
        missing = REQUIRED_TASK_FIELDS - set(task.keys())
        assert not missing, f"Task {task.get('id', '?')} missing fields: {missing}"


def test_unique_task_ids(tasks):
    ids = [t["id"] for t in tasks]
    assert len(ids) == len(set(ids)), f"Duplicate IDs: {[i for i in ids if ids.count(i) > 1]}"


def test_machines_are_valid(tasks):
    for task in tasks:
        for machine in task["machines"]:
            assert machine in VALID_MACHINES, (
                f"Task {task['id']} has unknown machine: {machine}"
            )


def test_scheduler_is_valid(tasks):
    for task in tasks:
        scheduler = task.get("scheduler", "cron")
        assert scheduler in VALID_SCHEDULERS, (
            f"Task {task['id']} has invalid scheduler: {scheduler}"
        )


def test_cron_schedule_format(tasks):
    """Cron tasks must have 5-field cron expressions."""
    for task in tasks:
        if task.get("scheduler", "cron") != "cron":
            continue
        parts = task["schedule"].split()
        assert len(parts) == 5, (
            f"Task {task['id']} schedule '{task['schedule']}' is not 5-field cron"
        )


def test_command_is_nonempty(tasks):
    for task in tasks:
        assert task["command"].strip(), f"Task {task['id']} has empty command"


def _invokes_claude_cli(command: str) -> bool:
    """Check if a command invokes the claude CLI (not just references .claude/ paths)."""
    import re
    return bool(re.search(r'\bclaude\b(?!\s*[/-])', command)) and \
        not all(m.start() == command.find('.claude') for m in re.finditer(r'\bclaude\b', command) if '.claude' in command[max(0,m.start()-1):m.start()+7])


def test_is_claude_task_field(tasks):
    """Tasks that invoke the claude CLI should have is_claude_task: true."""
    for task in tasks:
        if task.get("is_claude_task") is True:
            # If marked as claude task, that's fine — trust the annotation
            continue
        # Only flag if the command directly invokes `claude` as a CLI tool
        cmd = task["command"]
        # Simple heuristic: "claude " or "claude --" at word boundary, not ".claude/"
        import re
        if re.search(r'(?<!\.)(?<!/)\bclaude\s+--', cmd):
            assert task.get("is_claude_task") is True, (
                f"Task {task['id']} invokes claude CLI but is_claude_task != true"
            )


def test_linux_tasks_have_cron_scheduler(tasks):
    """Linux machines should use cron scheduler."""
    linux_machines = {"dev-primary", "dev-secondary", "gali-linux-compute-1"}
    for task in tasks:
        if set(task["machines"]) & linux_machines:
            assert task.get("scheduler", "cron") == "cron", (
                f"Task {task['id']} targets Linux machines but scheduler != cron"
            )


def test_windows_tasks_have_windows_scheduler(tasks):
    """Windows-only tasks should use windows-task-scheduler."""
    windows_machines = {"licensed-win-1", "licensed-win-2"}
    for task in tasks:
        if set(task["machines"]) <= windows_machines:
            assert task.get("scheduler", "cron") == "windows-task-scheduler", (
                f"Task {task['id']} targets only Windows but scheduler != windows-task-scheduler"
            )


def test_validator_script_passes():
    """The validator script itself should exit 0."""
    result = subprocess.run(
        ["uv", "run", "--no-project", "python", str(VALIDATOR)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, f"Validator failed:\n{result.stderr}\n{result.stdout}"


def test_dev_primary_has_comprehensive_learning(tasks):
    """Comprehensive learning must be scheduled on dev-primary."""
    found = any(
        t["id"] == "comprehensive-learning" and "dev-primary" in t["machines"]
        for t in tasks
    )
    assert found, "comprehensive-learning task not found for dev-primary"


def test_repo_sync_on_all_linux(tasks):
    """Repository sync should be on all Linux machines."""
    sync_tasks = [t for t in tasks if t["id"] == "repository-sync"]
    assert sync_tasks, "No repository-sync task found"
    machines = set()
    for t in sync_tasks:
        machines.update(t["machines"])
    assert "dev-primary" in machines
    assert "dev-secondary" in machines
