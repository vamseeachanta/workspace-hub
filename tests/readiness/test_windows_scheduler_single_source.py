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
CURATION_PS1 = REPO_ROOT / "scripts" / "curation" / "curate-session-memory.ps1"
SCHEDULE = REPO_ROOT / "config" / "scheduled-tasks" / "schedule-tasks.yaml"


def _equality_task() -> dict:
    tasks = yaml.safe_load(SCHEDULE.read_text())["tasks"]
    return next(task for task in tasks if task["id"] == "equality-report")


def _task(task_id: str) -> dict:
    tasks = yaml.safe_load(SCHEDULE.read_text())["tasks"]
    return next(task for task in tasks if task["id"] == task_id)


def test_setup_ps1_reads_schedule_yaml():
    text = SETUP_PS1.read_text()
    assert "schedule-tasks.yaml" in text
    assert "Get-EqualityReportTask" in text
    assert "Unknown Windows scheduler host" in text
    assert "RECONCILE_MACHINE" in text
    assert "Resolve-GitBash" in text


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


def test_windows_reconcile_and_curation_sources_are_declared():
    reconcile = _task("ecosystem-reconcile")
    assert reconcile["schedule"] == "15 5 * * *"
    assert set(reconcile["machines"]) >= {"ace-win-1", "ace-win-2"}
    assert "report-only" in reconcile["description"].lower()

    curation = _task("session-curation")
    assert curation["schedule"] == "47 */6 * * *"
    assert set(curation["machines"]) >= {"ace-win-1", "ace-win-2"}


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
    assert r"\Claude\SessionCuration" in result.stdout
    assert "every 6h at minute 47" in result.stdout
    assert r"\Claude\EcosystemReconcile" in result.stdout
    assert "daily 05:15" in result.stdout
    assert "scripts/windows/reconcile-ecosystem.ps1" in result.stdout


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
    assert 'Test-CommandAvailable -Name "bash"' not in text


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


def test_wrapper_prefers_uv_with_python_fallback():
    text = WRAPPER_PS1.read_text().lower()
    assert "python" in text
    assert 'get-command "uv"' in text
    assert 'invoke-checked -file "uv"' in text
    assert 'invoke-checked -file "python"' in text


def test_wrapper_refresh_matrix_is_opt_in_and_same_commit():
    text = WRAPPER_PS1.read_text()
    # Opt-in switch parameter (default off so scheduled runs stay state-only).
    assert "[switch]$RefreshMatrix" in text
    # Publishes the stable Pages alias alongside the dated report.
    assert "docs/reports/machine-equality-matrix.html" in text
    assert "Get-MatrixReportPaths" in text
    # Default mode discards the locally built matrix; refresh mode keeps + commits it.
    assert "if (-not $RefreshMatrix)" in text
    # Matrix HTML rides in the SAME equality commit (invariant preserved).
    assert "-RefreshMatrix:$RefreshMatrix" in text
    assert '"chore: equality report from $Machine"' in text
    assert '"chore: equality report from $machine"' not in text


def test_curation_restores_generated_matrix_preview():
    text = CURATION_PS1.read_text()
    assert "generated matrix path was already dirty before curation" in text
    assert "git restore --worktree -- $report" in text
    assert "Remove-Item -LiteralPath $report -Force" in text


def test_reconcile_log_prefers_public_machine_label():
    text = (REPO_ROOT / "scripts" / "windows" / "reconcile-ecosystem.ps1").read_text()
    assert "$Machine.ToLowerInvariant()" in text
    assert "$env:RECONCILE_MACHINE.ToLowerInvariant()" in text
