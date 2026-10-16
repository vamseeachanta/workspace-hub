import os
import re
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = REPO_ROOT / "scripts" / "operations" / "job-queue-windows"
WINDOWS_ONLY = pytest.mark.skipif(os.name != "nt", reason="Windows PowerShell required")


def run(cmd, cwd=None, env=None, check=True):
    merged = os.environ.copy()
    merged.update(env or {})
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        merged.pop(key, None)
    merged["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(cmd, cwd=cwd, env=merged, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise AssertionError(f"{cmd} failed\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def write_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def git(cmd, cwd, check=True):
    return run(["git", *cmd], cwd=cwd, check=check)


def make_repo(tmp_path, job_id="done"):
    queue = tmp_path / "queue"
    clones = tmp_path / "clones"
    worktrees = tmp_path / "worktrees"
    remote = tmp_path / "remote.git"
    for folder in (queue / "jobs", queue / "logs", queue / "locks", clones, worktrees):
        folder.mkdir(parents=True)
    git(["init", "--bare", str(remote)], tmp_path)
    clone = clones / "example-repo"
    git(["clone", str(remote), str(clone)], tmp_path)
    git(["config", "user.email", "tester" + "@" + "example.invalid"], clone)
    git(["config", "user.name", "Tester"], clone)
    write_text(clone / "README.md", "base\n")
    write_text(clone / ".gitignore", "private.bin\n.venv/\n")
    git(["add", "."], clone)
    git(["commit", "-m", "initial"], clone)
    git(["branch", "-M", "main"], clone)
    git(["push", "-u", "origin", "main"], clone)
    wt = worktrees / f"example-repo-cxl-{job_id}"
    git(["worktree", "add", "-b", f"jobs/run-{job_id}", str(wt), "origin/main"], clone)
    git(["push", "-u", "origin", f"jobs/run-{job_id}"], wt)
    write_text(queue / "jobs" / f"{job_id}.md", "REPO: example-repo\n")
    write_text(queue / "logs" / f"{job_id}.result", "OK abc pull\n")
    config = tmp_path / "job-queue.local.conf"
    write_text(config, "\n".join([
        f"QUEUE_ROOT={queue.as_posix()}", f"CLONE_ROOT={clones.as_posix()}",
        f"WORKTREE_ROOT={worktrees.as_posix()}", "JOB_BRANCH_PREFIX=jobs/run-",
        "DEFAULT_REPOSITORY=example-repo", "REPOSITORY_ALLOW_LIST=example-repo",
        "MIN_DISK_FREE_GB=50", "",
    ]))
    return queue, clones, worktrees, wt, config


def runner(config, command="cleanup", job_id="done", *extra):
    return run(["bash", str(SCRIPT_DIR / "run-job.sh"), command, job_id,
                "none", str(config), *extra], check=False)


def test_finished_pushed_clean_worktree_is_removed(tmp_path):
    _, _, _, wt, config = make_repo(tmp_path)
    assert runner(config).returncode == 0
    assert not wt.exists()


@pytest.mark.parametrize("state,reason", [
    ("unpublished", "head is not on its remote branch"),
    ("dirty", "changed or untracked files"),
    ("untracked", "changed or untracked files"),
    ("referenced", "named by pending work"),
    ("running", "job holds a lock slot"),
    ("wrong-branch", "worktree is not on the job branch"),
    ("detached", "worktree is detached"),
    ("ignored", "ignored item is not regenerable"),
    ("no-result", "job has no result line"),
])
def test_unsafe_worktrees_are_kept(tmp_path, state, reason):
    queue, _, _, wt, config = make_repo(tmp_path)
    if state == "unpublished":
        write_text(wt / "README.md", "unpublished\n")
        git(["add", "."], wt)
        git(["commit", "-m", "local change"], wt)
    elif state == "dirty":
        write_text(wt / "README.md", "changed\n")
    elif state == "untracked":
        write_text(wt / "new.txt", "new\n")
    elif state == "referenced":
        write_text(queue / "queue.txt", "later 1\n")
        write_text(queue / "jobs" / "later.md", "BASE_REF: jobs/run-done\n")
    elif state == "running":
        write_text(queue / "locks" / "slot1" / "owner", "done 123\n")
    elif state == "wrong-branch":
        git(["checkout", "-b", "other"], wt)
        git(["push", "-u", "origin", "other"], wt)
    elif state == "detached":
        git(["checkout", "--detach"], wt)
    elif state == "ignored":
        write_text(wt / "private.bin", "retain\n")
    elif state == "no-result":
        (queue / "logs" / "done.result").unlink()
    assert runner(config).returncode == 0
    assert wt.exists()
    assert reason in (queue / "logs" / "kept-worktrees.tsv").read_text()


def test_cleanup_dry_run_preserves_removable_worktree(tmp_path):
    _, _, _, wt, config = make_repo(tmp_path)
    result = runner(config, "cleanup", "done", "--dry-run")
    assert result.returncode == 0
    assert "would remove" in result.stdout
    assert wt.exists()


def test_cleanup_dry_run_reports_keep_reason(tmp_path):
    queue, _, _, wt, config = make_repo(tmp_path)
    write_text(wt / "new.txt", "retain\n")
    result = runner(config, "cleanup", "done", "--dry-run")
    assert result.returncode == 0
    assert "changed or untracked files" in result.stdout
    assert wt.exists()
    assert not (queue / "logs" / "kept-worktrees.tsv").exists()


def test_worktree_remove_refusal_is_recorded(tmp_path):
    queue, clones, _, wt, config = make_repo(tmp_path)
    git(["worktree", "lock", str(wt)], clones / "example-repo")
    assert runner(config).returncode == 0
    assert wt.exists()
    assert "git worktree remove refused" in (queue / "logs" / "kept-worktrees.tsv").read_text()


def test_git_status_failure_is_recorded_without_pending_file(tmp_path, monkeypatch):
    queue, _, _, wt, config = make_repo(tmp_path)
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    monkeypatch.setenv("TMPDIR", str(scratch))
    # An index with invalid bytes makes status fail while branch lookup still works.
    index = Path(git(["rev-parse", "--git-path", "index"], wt).stdout.strip())
    index.write_bytes(b"invalid index")
    assert runner(config).returncode == 0
    assert "git status failed" in (queue / "logs" / "kept-worktrees.tsv").read_text()
    assert not list(queue.glob("*pending*"))
    assert not list(scratch.iterdir())


def test_config_accepts_crlf_and_whitespace(tmp_path):
    _, _, _, wt, config = make_repo(tmp_path)
    config.write_bytes("\r\n".join(f"  {line.split('=', 1)[0]} = {line.split('=', 1)[1]}  "
                                    for line in config.read_text().splitlines()).encode() + b"\r\n")
    assert runner(config).returncode == 0
    assert not wt.exists()


def test_git_environment_bindings_are_not_inherited(tmp_path, monkeypatch):
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR"):
        monkeypatch.setenv(key, str(tmp_path / "unrelated"))
    assert git(["init", str(tmp_path / "fixture")], tmp_path).returncode == 0
    assert (tmp_path / "fixture" / ".git").is_dir()
    assert not (tmp_path / "unrelated").exists()


def test_path_limit_accepts_short_root_and_refuses_overlong_root(tmp_path):
    _, _, _, _, config = make_repo(tmp_path)
    assert runner(config, "path-check", "done", "README.md").returncode == 0
    bad = runner(config, "path-check", "done", "b" * 260)
    assert bad.returncode != 0
    assert "260 character limit" in bad.stdout


@pytest.mark.parametrize("repo", ["..", ".hidden"])
def test_dot_prefixed_repository_is_rejected(tmp_path, repo):
    queue, _, _, _, config = make_repo(tmp_path)
    write_text(queue / "jobs" / "done.md", f"REPO: {repo}\n")
    write_text(config, config.read_text().replace("REPOSITORY_ALLOW_LIST=example-repo", f"REPOSITORY_ALLOW_LIST={repo}"))
    assert runner(config, "path-check").returncode != 0


@WINDOWS_ONLY
@pytest.mark.parametrize("mode", ["clone", "worktree", "dry-run", "running", "probe-error", "slots", "per-repo"])
def test_pump_gates(tmp_path, mode):
    queue, _, _, _, config = make_repo(tmp_path)
    write_text(queue / "queue.txt", "first 1\nnext 2\n")
    for job_id in ("first", "next"):
        write_text(queue / "jobs" / f"{job_id}.md", "REPO: example-repo\n")
    launcher = tmp_path / "launcher.ps1"
    write_text(launcher, "throw 'launcher must not run'\n")
    clone, worktree = (49 if mode == "clone" else 999), (49 if mode == "worktree" else 999)
    probe = "{ throw 'probe failed' }" if mode == "probe-error" else f"{{ param($root,$role) if ($role -eq 'clone') {{ {clone} }} else {{ {worktree} }} }}"
    if mode in ("running", "slots", "per-repo"):
        write_text(queue / "locks" / "slot1" / "owner", "first 123\n")
    if mode == "slots":
        write_text(queue / "limits.txt", "max_running=1\n")
    if mode == "per-repo":
        write_text(queue / "limits.txt", "per_repo_max=1\n")
    command = f"& '{(SCRIPT_DIR / 'pump.ps1').as_posix()}' -ConfigPath '{config.as_posix()}' -DryRun -FreeSpaceProbe {probe} -Launcher '{launcher.as_posix()}'"
    run(["powershell", "-NoProfile", "-Command", command])
    log = (queue / "pump.log").read_text()
    expected = {"clone": "reason=clone-disk-under-50GB", "worktree": "reason=worktree-disk-under-50GB",
                "dry-run": "action=would-start job=first", "running": "action=would-start job=next",
                "probe-error": "reason=disk-probe-failed", "slots": "reason=max-running",
                "per-repo": "reason=queue-empty-or-all-started"}[mode]
    assert expected in log


def test_public_scripts_and_install_contract():
    text = "\n".join(path.read_text() for path in SCRIPT_DIR.iterdir() if path.is_file())
    assert not re.search(r"[A-Za-z]:[\\/]", text)
    assert "<queue-root>" in text
    assert "REPOSITORY_OWNER" not in text
    assert "JOB_BRANCH_PREFIX" in text
    pump = (SCRIPT_DIR / "pump.ps1").read_text()
    assert "JOB_QUEUE_TEST_" not in pump
    assert "[switch]$Once" not in pump
    install = (SCRIPT_DIR / "INSTALL.md").read_text()
    assert "Do not copy" in install
    assert "cleanup" in install and "-DryRun" in install


def disk_probe_fixture(tmp_path, monkeypatch, available):
    tools = tmp_path / "tools"
    probe = tools / "df"
    write_text(probe, f"#!/usr/bin/env bash\nprintf 'disk 999 0 {available} 0%% root\\n'\n")
    probe.chmod(int("755", 8))
    monkeypatch.setenv("PATH", str(tools) + os.pathsep + os.environ["PATH"])


@pytest.mark.parametrize("available", ["1", "invalid"])
def test_direct_start_refuses_low_or_invalid_disk_probe(tmp_path, monkeypatch, available):
    queue, _, worktrees, _, config = make_repo(tmp_path)
    write_text(queue / "jobs" / "new.md", "REPO: example-repo\n")
    disk_probe_fixture(tmp_path, monkeypatch, available)
    result = runner(config, "start", "new")
    assert result.returncode != 0
    assert "blocked: disk" in result.stdout
    assert not (worktrees / "example-repo-cxl-new").exists()


def test_direct_start_uses_configured_branch(tmp_path, monkeypatch):
    queue, _, worktrees, _, config = make_repo(tmp_path)
    write_text(queue / "jobs" / "new.md", "REPO: example-repo\n")
    disk_probe_fixture(tmp_path, monkeypatch, "999999999")
    result = runner(config, "start", "new")
    assert result.returncode == 0
    wt = worktrees / "example-repo-cxl-new"
    assert git(["branch", "--show-current"], wt).stdout.strip() == "jobs/run-new"


def test_start_path_limit_uses_requested_base_tree(tmp_path, monkeypatch):
    queue, clones, worktrees, _, config = make_repo(tmp_path)
    clone = clones / "example-repo"
    git(["checkout", "-b", "alternate"], clone)
    write_text(clone / ("long-" + "x" * 200), "long path\n")
    git(["add", "."], clone)
    git(["commit", "-m", "long base path"], clone)
    git(["push", "-u", "origin", "alternate"], clone)
    git(["checkout", "main"], clone)
    write_text(queue / "jobs" / "new.md", "REPO: example-repo\nBASE_REF: alternate\n")
    disk_probe_fixture(tmp_path, monkeypatch, "999999999")
    result = runner(config, "start", "new")
    assert result.returncode != 0
    assert "260 character limit" in result.stdout
    assert not (worktrees / "example-repo-cxl-new").exists()


@WINDOWS_ONLY
def test_powershell_scripts_parse(tmp_path):
    for path in SCRIPT_DIR.glob("*.ps1"):
        command = f"$tokens=$null; $errors=$null; [void][System.Management.Automation.Language.Parser]::ParseFile('{path.as_posix()}', [ref]$tokens, [ref]$errors); if ($errors.Count) {{ throw ($errors | Out-String) }}"
        run(["powershell", "-NoProfile", "-Command", command])


@WINDOWS_ONLY
def test_launcher_quotes_paths_and_forwards_config(tmp_path):
    import shutil
    import time

    folder = tmp_path / "scripts with spaces and 'quote"
    folder.mkdir()
    shutil.copyfile(SCRIPT_DIR / "launch.ps1", folder / "launch.ps1")
    queue = tmp_path / "queue with spaces"
    (queue / "logs").mkdir(parents=True)
    config = tmp_path / "config with 'quote.conf"
    write_text(config, f"QUEUE_ROOT={queue.as_posix()}\n")
    write_text(folder / "capture.sh", '#!/usr/bin/env bash\nprintf "%s\\n" "$@"\n')
    run(["powershell", "-NoProfile", "-File", str(folder / "launch.ps1"),
         "-ConfigPath", str(config), "-Script", "capture.sh", "-A1", "test", "-A2", "1"])
    output = queue / "logs" / "test.launch.out"
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if output.exists() and len(output.read_text().splitlines()) == 4:
            break
        time.sleep(0.1)
    assert output.read_text().splitlines() == ["start", "test", "1", config.as_posix()]


def test_cleanup_accepts_completed_queue_entries(tmp_path):
    queue, _, _, wt, config = make_repo(tmp_path)
    write_text(queue / "queue.txt", "done 1\n")
    result = runner(config)
    assert result.returncode == 0
    assert not wt.exists()


def test_cleanup_accepts_leading_dry_run_switch(tmp_path):
    _, _, _, wt, config = make_repo(tmp_path)
    result = run(["bash", str(SCRIPT_DIR / "run-job.sh"), "cleanup", "--dry-run",
                  "done", "none", str(config)], check=False)
    assert result.returncode == 0
    assert "would remove" in result.stdout
    assert wt.exists()
