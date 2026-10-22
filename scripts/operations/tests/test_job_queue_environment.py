"""Repository selection must not inherit the launching shell's Git bindings."""

import hashlib
import os
import subprocess

import pytest
from test_job_queue_windows import (
    SCRIPT_DIR,
    disk_probe_fixture,
    git,
    make_repo,
    write_text,
)


def snapshot(root):
    """Include tracked files and Git metadata, not only the visible checkout."""
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in root.rglob("*") if path.is_file()
    }


@pytest.mark.parametrize("command", ["start", "cleanup", "cleanup-recent"])
@pytest.mark.parametrize("binding", ["GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "all"])
def test_runner_uses_configured_repository(tmp_path, monkeypatch, command, binding):
    """Independent oracle: only the configured worktree may change.

    For start, the new branch belongs to the configured clone. For cleanup,
    the finished fixture is removed. The caller's complete byte digest map
    remains equal before and after every command, including Git metadata.
    """
    queue, clones, worktrees, wt, config = make_repo(tmp_path)
    caller = tmp_path / "caller"
    git(["clone", "--branch", "main", str(tmp_path / "remote.git"), str(caller)], tmp_path)
    write_text(caller / "retain.txt", "caller evidence\n")
    before = snapshot(caller)
    env = os.environ.copy()
    bindings = {
        "GIT_DIR": str(caller / ".git"),
        "GIT_WORK_TREE": str(caller),
        "GIT_COMMON_DIR": str(caller / ".git"),
    }
    # Pass contaminated values directly: the shared test helper clears them.
    for key in bindings:
        env.pop(key, None)
    env.update(bindings if binding == "all" else {binding: bindings[binding]})
    job = "done"
    if command == "start":
        job = "new"
        write_text(queue / "jobs" / "new.md", "REPO: example-repo\n")
        # Synthetic disk measurement; floor boundaries are covered separately.
        disk_probe_fixture(tmp_path, monkeypatch, "999999999")
        env["PATH"] = os.environ["PATH"]
    elif command == "cleanup-recent":
        marker = queue / "logs" / "recent-cleanup" / "done"
        write_text(marker, "")
        # Epoch time is unambiguously outside the configured retention window.
        os.utime(marker, (0, 0))
        job = "all"
    result = subprocess.run(
        ["bash", str(SCRIPT_DIR / "run-job.sh"), command, job, "none", str(config)],
        cwd=caller, env=env, text=True, capture_output=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert snapshot(caller) == before
    if command == "start":
        created = worktrees / "example-repo-cxl-new"
        assert created.exists()
        assert git(["branch", "--show-current"], created).stdout.strip() == "jobs/run-new"
        common = git(["rev-parse", "--git-common-dir"], created).stdout.strip()
        assert os.path.samefile(common, clones / "example-repo" / ".git")
    else:
        assert not wt.exists(), result.stdout + result.stderr
