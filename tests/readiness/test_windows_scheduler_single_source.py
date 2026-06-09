"""Contract tests for the Windows equality Task Scheduler renderer (#2815)."""

from __future__ import annotations

import shutil
import subprocess
import os
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SETUP_PS1 = REPO_ROOT / "scripts" / "windows" / "setup-scheduler-tasks.ps1"
WRAPPER_PS1 = REPO_ROOT / "scripts" / "windows" / "equality-report.ps1"
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"


def _equality_task() -> dict:
    tasks = yaml.safe_load(SCHEDULE.read_text())["tasks"]
    return next(task for task in tasks if task["id"] == "equality-report")


def test_setup_ps1_reads_schedule_yaml():
    text = SETUP_PS1.read_text()
    assert "schedule-tasks.yaml" in text
    assert "Get-EqualityReportTask" in text
    assert "Unknown Windows scheduler host" in text


def test_setup_ps1_has_no_hardcoded_equality_schedule_or_uv():
    text = SETUP_PS1.read_text()
    assert "30 4 * * 1" not in text
    match = re.search(r'-Name "EqualityReport".*?(?=\n\} else|\Z)', text, re.S)
    assert match, "EqualityReport registration block not found"
    equality_block = match.group(0)
    assert "-CronSchedule $equalityTask.Schedule" in equality_block
    assert "-DailyAt" not in equality_block
    assert "uv run" not in text.lower()


def test_equality_task_source_is_weekly_monday():
    task = _equality_task()
    minute, hour, day_of_month, month, day_of_week = task["schedule"].split()
    assert (minute, hour, day_of_month, month, day_of_week) == ("30", "4", "*", "*", "1")
    for machine in ("ace-win-1", "ace-win-2"):
        assert machine in task["machines"]


def test_setup_whatif_renders_equality_report_as_weekly_monday():
    if os.name != "nt":
        pytest.skip("Windows ScheduledTasks cmdlets are required")
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if powershell is None:
        pytest.skip("PowerShell is required to execute the Windows renderer")

    result = subprocess.run(
        [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SETUP_PS1), "-WhatIf"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, result.stderr
    assert r"\Claude\EqualityReport" in result.stdout
    assert "weekly Monday 04:30" in result.stdout
    assert "scripts/windows/equality-report.ps1" in result.stdout


def test_wrapper_invokes_collector_builder_and_state_sync():
    text = WRAPPER_PS1.read_text()
    assert "collect-equality.ps1" in text
    assert "build-equality-matrix.py" in text
    assert ".claude/state/equality-<machine>.yaml" in text
    assert 'equality-$Machine.yaml' in text
    assert ".claude/state/equality-*.yaml" not in text
    assert "logs\\quality" in text
    assert "Invoke-EqualityTranscript" in text
    assert "Start-Transcript" in text
    assert "Stop-Transcript" in text
    assert "git" in text
    assert "commit" in text
    assert "push" in text


def test_wrapper_recovers_existing_equality_commits_only():
    text = WRAPPER_PS1.read_text()
    assert "Push-ExistingEqualityCommit" in text
    assert "Invoke-ExistingEqualityCommitRebase" in text
    assert "Test-AheadCommitIsEqualityReport" in text
    assert "^chore: equality report from " in text
    assert "git diff-tree --no-commit-id --name-only -r" in text
    assert "non-equality commits; refusing to push" in text
    assert "git rebase origin/main" in text
    assert "Push-ExistingEqualityCommit -Branch $Branch -Machine $Machine -Ahead $ahead" in text
    assert '"commit", "--amend", "--only"' in text


def test_wrapper_runs_from_main_only():
    text = WRAPPER_PS1.read_text()
    assert 'EqualityReport must run from main' in text
    assert "Unknown Windows equality host" in text
    assert "acma-ws014" in text


def test_wrapper_commit_and_matrix_dirty_guards_are_path_scoped():
    text = WRAPPER_PS1.read_text()
    assert '"commit", "--only"' in text
    assert '"commit", "--amend", "--only"' in text
    assert "Confirm-MatrixReportClean" in text
    assert "Clear-GeneratedMatrixReport" in text
    assert "git pull --rebase" not in text


def test_wrapper_uses_python_not_uv():
    text = WRAPPER_PS1.read_text().lower()
    assert "python" in text
    assert "uv" not in text
