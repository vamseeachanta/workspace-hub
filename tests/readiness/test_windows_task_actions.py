"""Regression contracts for unattended task actions; no scheduler is mutated."""
from pathlib import Path
import os
import subprocess

ROOT = Path(__file__).resolve().parents[2]
WINDOWS = ROOT / "scripts/windows"
CONTEXT = ROOT / "scripts/coordination/context"


def test_preview_precedes_scheduler_objects():
    text = (WINDOWS / "setup-scheduler-tasks.ps1").read_text()
    registration = text[text.index("function Register-"):text.index("if (-not $WhatIf -and")]
    assert "[Alias('DryRun')]" in text
    preview = registration.index("ConvertTo-Json")
    assert preview < registration.index("New-ScheduledTaskAction")
    assert preview < registration.index("ConvertTo-TaskTrigger -Spec")
    assert preview < registration.index("Get-DefaultTaskSetting\n")
    assert "WorkingDirectory" in registration
    assert "New-RepoTaskDefinition" in registration


def test_shared_action_is_absolute_and_policy_preserving():
    text = (WINDOWS / "scheduler-actions.ps1").read_text()
    assert "Resolve-RepoTaskScript" in text
    assert "Join-Path $PSHOME" in text
    assert "-NoProfile -File" in text
    assert "ExecutionPolicy" not in text
    assert "ToBase64String" in text
    assert "LogPattern" in text
    assert "WorkingDirectory = $WorkspaceRoot" in text
    resolver = (WINDOWS / "scheduler-yaml.ps1").read_text()
    assert "return $full" in resolver


def test_runner_captures_output_and_exit_code():
    text = (WINDOWS / "run-scheduled-task.ps1").read_text()
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
    text = (WINDOWS / "setup-scheduler-tasks.ps1").read_text()
    assert '-ScriptPath "scripts/coordination/context/daily_context_check.sh"' in text
    assert "daily_context_check.bat" not in text
    for pattern in ("logs/quality/equality-*.log", "logs/monitoring/session-curation-*.log",
                    "logs/quality/reconcile-*.log", "logs/monitoring/equivalence-sentinel-*.log"):
        assert pattern in text
    for path in (WINDOWS / "setup-scheduler-tasks.ps1", WINDOWS / "schedule-equivalence-tasks.sh",
                 WINDOWS / "equality-report.ps1", CONTEXT / "setup_scheduled_task.ps1"):
        assert "ExecutionPolicy" not in path.read_text()
    context = (CONTEXT / "setup_scheduled_task.ps1").read_text()
    assert "New-RepoTaskDefinition" in context
    assert "ConvertTo-Json" in context
    assert 'Resolve-Path' in context


def test_curation_uses_child_powershell_for_exiting_collector():
    text = (ROOT / "scripts/curation/curate-session-memory.ps1").read_text()
    assert "& $collector" not in text
    assert "'-NoProfile', '-File', $collector" in text
    assert "& $childPowerShell @collectorArguments" in text
    assert "(Get-Process -Id $PID).Path" in text


def _copy_context(tmp_path):
    root = tmp_path / "repo with spaces"
    scripts = root / "scripts/coordination/context"
    scripts.mkdir(parents=True)
    for name in ("daily_context_check.sh", "analyze_patterns.sh"):
        (scripts / name).write_text((CONTEXT / name).read_text())
    return root, scripts


def test_context_derives_and_exports_root_from_script(tmp_path):
    root, scripts = _copy_context(tmp_path)
    for name in ("validate_context.sh", "analyze_patterns.sh", "improve_context.sh"):
        (scripts / name).write_text('printf "ROOT=%s\\n" "$WORKSPACE_ROOT"\n')
    env = dict(os.environ)
    env.pop("WORKSPACE_ROOT", None)
    result = subprocess.run(["bash", str(scripts / "daily_context_check.sh")],
                            cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    reports = list((root / ".claude/reports").glob("context-health-*.md"))
    assert len(reports) == 1
    assert reports[0].read_text().count(f"ROOT={root}") == 3


def test_pattern_analysis_survives_first_repository(tmp_path):
    root, scripts = _copy_context(tmp_path)
    (root / "sample/.git").mkdir(parents=True)
    env = dict(os.environ, WORKSPACE_ROOT=str(root))
    result = subprocess.run(["bash", str(scripts / "analyze_patterns.sh"), "7"],
                            cwd=tmp_path, env=env, text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
    assert "repos_analyzed: 1" in (root / ".claude/state/context-patterns.yaml").read_text()


def test_workstation_readiness_preserves_following_sections(tmp_path):
    root = tmp_path / "repo with spaces"
    log = root / "logs/daily"
    log.mkdir(parents=True)
    from datetime import date
    report = log / f"{date.today().isoformat()}.md"
    report.write_text("# Daily\n\n## Readiness\nold content\n\n## Following\nkeep this\n")
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
    text = report.read_text()
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
    text = (CONTEXT / "daily_context_check.bat").read_text()
    assert "%~dp0" in text
    assert "where git.exe" in text
    assert "where bash" not in text
    assert "exit /b %ERRORLEVEL%" in text
