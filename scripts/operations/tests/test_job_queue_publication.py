"""Cleanup publication evidence is checked against a disposable remote."""

import os
import shlex
import shutil

import pytest

from test_job_queue_windows import (
    SCRIPT_DIR, age_worktree, git, make_repo, run, runner, write_text,
)


@pytest.mark.parametrize("dry_run", [False, True])
def test_deleted_remote_branch_is_kept_despite_tracking_ref(tmp_path, dry_run):
    """Hand check: the remote has no job ref, so publication is unestablished."""
    queue, _, _, wt, config = make_repo(tmp_path)
    git(["push", "origin", "--delete", "jobs/run-done"], wt)
    head = git(["rev-parse", "HEAD"], wt).stdout.strip()
    git(["update-ref", "refs/remotes/origin/jobs/run-done", head], wt)
    age_worktree(wt)
    result = runner(config, "cleanup", "done", *(["--dry-run"] if dry_run else []))
    assert result.returncode == 0
    assert wt.exists()
    log = result.stdout if dry_run else (queue / "logs/kept-worktrees.tsv").read_text()
    assert "head is not on its remote branch" in log


def test_unreachable_remote_is_kept_despite_tracking_ref(tmp_path):
    """A local tracking ref is historical evidence, not a current remote probe."""
    queue, _, _, wt, config = make_repo(tmp_path)
    git(["remote", "set-url", "origin", str(tmp_path / "absent.git")], wt)
    age_worktree(wt)
    assert runner(config).returncode == 0
    assert wt.exists()
    assert "head is not on its remote branch" in (queue / "logs/kept-worktrees.tsv").read_text()


@pytest.mark.parametrize("record", ["FAIL execution\n", "FAIL execution\nOK later\n", "OKAY\n"])
def test_failed_result_is_retained(tmp_path, record):
    """Issue cleanup criterion requires a finished, published job; failure is kept."""
    queue, _, _, wt, config = make_repo(tmp_path)
    write_text(queue / "logs/done.result", record)
    assert runner(config).returncode == 0
    assert wt.exists()
    assert "job result is not successful" in (queue / "logs/kept-worktrees.tsv").read_text()


def test_empty_result_is_retained(tmp_path):
    queue, _, _, wt, config = make_repo(tmp_path)
    write_text(queue / "logs/done.result", "")
    assert runner(config).returncode == 0
    assert wt.exists()


@pytest.mark.parametrize("delta", [-1, 0, 1])
def test_pump_disk_probe_preserves_floor_boundary(tmp_path, delta):
    """Issue 4081 floor: one byte below fails, equality and one byte above pass.

    The existing binary unit convention is retained: GiB = 2**30 bytes.
    Expected comparison follows directly from the sign of the added byte.
    """
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if not powershell:
        pytest.skip("PowerShell required for production disk probe")
    script = tmp_path / "disk-boundary.ps1"
    write_text(script, f'''
$ErrorActionPreference = 'Stop'
$ast = [System.Management.Automation.Language.Parser]::ParseFile(
  '{SCRIPT_DIR / "pump.ps1"}', [ref]$null, [ref]$null)
$ast.FindAll({{ param($node)
  $node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
    $node.Name -eq 'Get-FreeDiskGb'
}}, $false) | ForEach-Object {{ Invoke-Expression $_.Extent.Text }}
function New-Object {{ [pscustomobject]@{{ AvailableFreeSpace = (50 * 1GB) + ({delta}) }} }}
$actual = Get-FreeDiskGb '{tmp_path}' 'worktree'
if (($actual -ge 50) -ne ${str(delta >= 0).lower()}) {{ throw 'floor comparison changed' }}
''')
    run([powershell, "-NoProfile", "-File", str(script)])


def test_runner_uses_live_remote_even_with_cached_ref(tmp_path, monkeypatch):
    _, _, _, wt, config = make_repo(tmp_path)
    calls = tmp_path / "remote-probe.txt"
    tools = tmp_path / "tools"
    real_git = shutil.which("git")
    write_text(tools / "git", f'''#!/usr/bin/env bash
if [[ "$*" == *'ls-remote origin'* ]]; then
  printf 'probe\\n' >> {shlex.quote(str(calls))}
fi
exec {shlex.quote(real_git)} "$@"
''')
    (tools / "git").chmod(0o755)
    monkeypatch.setenv("PATH", str(tools) + os.pathsep + os.environ["PATH"])
    assert runner(config).returncode == 0
    assert not wt.exists()
    assert calls.read_text().splitlines() == ["probe"]
