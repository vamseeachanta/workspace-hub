"""Regression contracts for unattended task actions; no scheduler is mutated."""
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WINDOWS = ROOT / "scripts/windows"
CONTEXT = ROOT / "scripts/coordination/context"


def test_preview_precedes_scheduler_objects():
    text = (WINDOWS / "setup-scheduler-tasks.ps1").read_text(encoding="utf-8")
    registration = text[text.index("function Register-"):text.index("if (-not $WhatIf -and")]
    assert "[Alias('DryRun')]" in text
    preview = registration.index("ConvertTo-Json")
    assert preview < registration.index("New-ScheduledTaskAction")
    assert preview < registration.index("ConvertTo-TaskTrigger -Spec")
    assert preview < registration.index("Get-DefaultTaskSetting\n")
    assert "WorkingDirectory" in registration
    assert "New-RepoTaskDefinition" in registration


def test_shared_action_is_absolute_and_policy_preserving():
    text = (WINDOWS / "scheduler-actions.ps1").read_text(encoding="utf-8")
    assert "Resolve-RepoTaskScript" in text
    assert "Join-Path $PSHOME" in text
    assert "-NoProfile -File" in text
    assert "ExecutionPolicy" not in text
    assert "ToBase64String" in text
    assert "LogPattern" in text
    assert "WorkingDirectory = $WorkspaceRoot" in text
    resolver = (WINDOWS / "scheduler-yaml.ps1").read_text(encoding="utf-8")
    assert "return $full" in resolver


def test_runner_captures_output_and_exit_code():
    text = (WINDOWS / "run-scheduled-task.ps1").read_text(encoding="utf-8")
    assert "Set-Location -LiteralPath" in text
    assert "2>&1" in text
    assert "-Append" in text
    assert "exit $result" in text
    assert "$LASTEXITCODE" in text
    assert "ExecutionPolicy" not in text
    assert "-NoProfile" in text and "'-File'" in text
    assert "ERROR:" in text
    assert "yyyy-MM-dd-HHmmss-fff" in text


def test_all_installed_scripts_have_logs_and_correct_interpreters():
    text = (WINDOWS / "setup-scheduler-tasks.ps1").read_text(encoding="utf-8")
    assert '-ScriptPath "scripts/coordination/context/daily_context_check.sh"' in text
    assert "daily_context_check.bat" not in text
    for pattern in ("logs/quality/equality-*.log", "logs/monitoring/session-curation-*.log",
                    "logs/quality/reconcile-*.log", "logs/monitoring/equivalence-sentinel-*.log"):
        assert pattern in text
    for path in (WINDOWS / "setup-scheduler-tasks.ps1", WINDOWS / "schedule-equivalence-tasks.sh",
                 WINDOWS / "equality-report.ps1", CONTEXT / "setup_scheduled_task.ps1"):
        assert "ExecutionPolicy" not in path.read_text(encoding="utf-8")
    context = (CONTEXT / "setup_scheduled_task.ps1").read_text(encoding="utf-8")
    assert "New-RepoTaskDefinition" in context
    assert "ConvertTo-Json" in context
    assert 'Resolve-Path' in context


def test_curation_uses_child_powershell_for_exiting_collector():
    text = (ROOT / "scripts/curation/curate-session-memory.ps1").read_text(encoding="utf-8")
    assert "& $collector" not in text
    assert "'-NoProfile', '-File', $collector" in text
    assert "& $childPowerShell @collectorArguments" in text
    assert "(Get-Process -Id $PID).Path" in text


def _copy_context(tmp_path):
    root = tmp_path / "repo with spaces"
    scripts = root / "scripts/coordination/context"
    scripts.mkdir(parents=True)
    for name in ("daily_context_check.sh", "analyze_patterns.sh"):
        (scripts / name).write_text((CONTEXT / name).read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    return root, scripts


def test_context_derives_and_exports_root_from_script(tmp_path):
    root, scripts = _copy_context(tmp_path)
    for name in ("validate_context.sh", "analyze_patterns.sh", "improve_context.sh"):
        (scripts / name).write_text('printf "ROOT=%s\\n" "$WORKSPACE_ROOT"\n', encoding="utf-8", newline="\n")
    env = dict(os.environ)
    env.pop("WORKSPACE_ROOT", None)
    result = subprocess.run(["bash", str(scripts / "daily_context_check.sh")],
                            cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    reports = list((root / ".claude/reports").glob("context-health-*.md"))
    assert len(reports) == 1
    assert reports[0].read_text(encoding="utf-8").count(f"ROOT={root}") == 3


def test_pattern_analysis_survives_first_repository(tmp_path):
    root, scripts = _copy_context(tmp_path)
    (root / "sample/.git").mkdir(parents=True)
    env = dict(os.environ, WORKSPACE_ROOT=str(root))
    result = subprocess.run(["bash", str(scripts / "analyze_patterns.sh"), "7"],
                            cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "repos_analyzed: 1" in (root / ".claude/state/context-patterns.yaml").read_text(encoding="utf-8")


def test_workstation_readiness_preserves_following_sections(tmp_path):
    root = tmp_path / "repo with spaces"
    log = root / "logs/daily"
    log.mkdir(parents=True)
    from datetime import date
    report = log / f"{date.today().isoformat()}.md"
    report.write_text("# Daily\n\n## Readiness\nold content\n\n## Following\nkeep this\n", encoding="utf-8", newline="\n")
    ansys = tmp_path / "installed analysis/v252"
    ansys.mkdir(parents=True)
    orca = tmp_path / "installed dynamics/11.6"
    orca.mkdir(parents=True)
    (orca / "OrcaFlex64.exe").touch()
    env = dict(os.environ, WORKSPACE_HUB=str(root), ANSYS_ROOT=str(ansys.parent),
               ORCAFLEX_ROOT=str(orca.parent))
    result = subprocess.run(["bash", str(ROOT / "scripts/readiness/workstation-version-check.sh")],
                            env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stdout + result.stderr
    text = report.read_text(encoding="utf-8")
    assert "## Following\nkeep this" in text
    assert "old content" not in text
    assert text.count("## Readiness") == 1


def test_workstation_missing_installations_still_fail(tmp_path):
    env = dict(os.environ, WORKSPACE_HUB=str(tmp_path / "repository"),
               ANSYS_ROOT=str(tmp_path / "missing analysis"),
               ORCAFLEX_ROOT=str(tmp_path / "missing dynamics"))
    result = subprocess.run(["bash", str(ROOT / "scripts/readiness/workstation-version-check.sh")],
                            env=env, text=True, capture_output=True)
    assert result.returncode == 1
    assert "2/2 checks failed" in result.stdout


def test_context_batch_compatibility_cannot_select_wsl_bash():
    text = (CONTEXT / "daily_context_check.bat").read_text(encoding="utf-8")
    assert "%~dp0" in text
    assert "where git.exe" in text
    assert "where bash" not in text
    assert "exit /b %ERRORLEVEL%" in text


def test_task_regressions_are_registered_in_family_inventory():
    import json

    inventory = json.loads((ROOT / "config/ci/hub-test-families.json").read_text(encoding="utf-8"))
    path = Path(__file__).relative_to(ROOT).as_posix()
    assert path in inventory["families"]["tests/readiness"]
    assert inventory["file_count"] == sum(len(paths) for paths in inventory["families"].values())


def test_windows_ci_executes_behavioral_harness_for_draft_updates():
    import yaml

    workflow = yaml.safe_load((ROOT / ".github/workflows/windows-task-actions.yml").read_text(encoding="utf-8"))
    # PyYAML interprets the YAML 1.1 key "on" as True.
    events = workflow.get("on", workflow.get(True))
    assert "synchronize" in events["pull_request"]["types"]
    job = workflow["jobs"]["windows-task-actions"]
    assert job["runs-on"] == "windows-latest"
    assert "if" not in job
    steps = job["steps"]
    assert any(step.get("uses") == "actions/checkout@v4" for step in steps)
    run = next(step for step in steps if "windows-task-actions.ps1" in step.get("run", ""))
    assert run["shell"] == "powershell"
    assert "-ScratchDirectory" in run["run"]
    assert "$env:RUNNER_TEMP" in run["run"]
    assert "continue-on-error" not in job
    assert "continue-on-error" not in run
    assert "if" not in run


def test_behavioral_harness_reports_success_after_expected_child_failures():
    harness = (ROOT / "tests/readiness/windows-task-actions.ps1").read_text(encoding="utf-8")
    assert harness.rstrip().endswith("exit 0")
    assert "Set-Content" not in harness
    assert "[IO.File]::WriteAllText" in harness
    assert '.Replace("`r`n", "`n")' in harness
