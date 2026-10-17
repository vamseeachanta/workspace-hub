"""Deferred cleanup uses only disposable repositories and aged retry markers."""

import os
import time

import pytest

from test_job_queue_windows import (
    SCRIPT_DIR, WINDOWS_ONLY, age_worktree, fake_git_fixture, git,
    make_repo, run, runner, write_text,
)


def retry_path(queue, job_id="done"):
    return queue / "logs" / "recent-cleanup" / job_id


def age_retry(queue, job_id="done", minutes=120):
    marker = retry_path(queue, job_id)
    stamp = time.time() - minutes * 60
    os.utime(marker, (stamp, stamp))


def retain_recent(tmp_path):
    queue, clones, roots, wt, config = make_repo(tmp_path)
    (wt / "README.md").touch()
    write_text(queue / "logs" / "done.result", "OK published\n")
    assert runner(config).returncode == 0
    assert wt.exists()
    assert retry_path(queue).is_file()
    return queue, clones, roots, wt, config


def test_immediate_retention_then_eventual_removal(tmp_path):
    queue, _, _, wt, config = retain_recent(tmp_path)
    assert runner(config, "cleanup-recent", "all").returncode == 0
    assert wt.exists()  # No retry while the initial activity window is open.
    age_worktree(wt)
    age_retry(queue)
    result = runner(config, "cleanup-recent", "all")
    assert result.returncode == 0, result.stderr
    assert not wt.exists()
    assert not retry_path(queue).exists()
    assert runner(config, "cleanup-recent", "all").returncode == 0


@pytest.mark.parametrize("state,reason", [
    ("recent-file", "worktree was touched recently"),
    ("recent-admin", "worktree was touched recently"),
    ("locked", "worktree is locked"),
    ("pending", "named by pending work"),
    ("running", "job holds a lock slot"),
    ("activity-failure", "worktree activity probe failed"),
    ("lock-failure", "git worktree lock lookup failed"),
    ("dirty", "changed or untracked files"),
    ("no-result", "job has no result line"),
])
def test_later_pass_rechecks_guards(tmp_path, monkeypatch, state, reason):
    queue, clones, _, wt, config = retain_recent(tmp_path)
    age_worktree(wt)
    age_retry(queue)
    if state == "recent-file":
        (wt / "README.md").touch()
    elif state == "recent-admin":
        admin = git(["rev-parse", "--absolute-git-dir"], wt).stdout.strip()
        os.utime(admin, None)
    elif state == "locked":
        git(["worktree", "lock", str(wt)], clones / "example-repo")
    elif state == "pending":
        write_text(queue / "queue.txt", "later 1\n")
        write_text(queue / "jobs" / "later.md", "BASE_REF: jobs/run-done\n")
    elif state == "running":
        write_text(queue / "locks" / "slot1" / "owner", "done 123\n")
    elif state == "dirty":
        write_text(wt / "README.md", "changed\n")
    elif state == "no-result":
        (queue / "logs" / "done.result").unlink()
    calls = fake_git_fixture(tmp_path, monkeypatch, wt, state)
    result = runner(config, "cleanup-recent", "all")
    assert result.returncode == 0, result.stderr
    assert wt.exists()
    assert reason in (queue / "logs" / "kept-worktrees.tsv").read_text()
    if calls.exists():
        assert "worktree remove" not in calls.read_text()
    assert retry_path(queue).exists() == state.startswith("recent-")


@pytest.mark.parametrize("dry_run", [False, True])
def test_only_recent_activity_is_enrolled(tmp_path, dry_run):
    queue, _, _, wt, config = make_repo(tmp_path)
    (wt / "README.md").touch()
    write_text(wt / "untracked.txt", "retain\n")
    assert runner(config, "cleanup", "done", *(["--dry-run"] if dry_run else [])).returncode == 0
    assert not retry_path(queue).exists()


def test_later_dry_run_preserves_tree_log_and_marker(tmp_path):
    queue, _, _, wt, config = retain_recent(tmp_path)
    age_worktree(wt)
    age_retry(queue)
    marker = retry_path(queue)
    log = queue / "logs" / "kept-worktrees.tsv"
    before = (marker.read_bytes(), marker.stat().st_mtime_ns, log.read_bytes())
    result = runner(config, "cleanup-recent", "all", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "would remove: done" in result.stdout
    assert wt.exists()
    assert (marker.read_bytes(), marker.stat().st_mtime_ns, log.read_bytes()) == before


def test_repeated_recent_cleanup_does_not_grow_keep_log(tmp_path):
    queue, _, _, _, config = retain_recent(tmp_path)
    log = queue / "logs" / "kept-worktrees.tsv"
    before = log.read_bytes()
    for _ in range(3):
        assert runner(config).returncode == 0
    assert log.read_bytes() == before


@pytest.mark.parametrize("minutes,removed", [(10, True), (90, False)])
def test_later_pass_uses_configured_window(tmp_path, monkeypatch, minutes, removed):
    queue, _, _, wt, config = retain_recent(tmp_path)
    age_worktree(wt, minutes=30)
    age_retry(queue, minutes=30)
    monkeypatch.setenv("WORKTREE_KEEP_MINUTES", str(minutes))
    assert runner(config, "cleanup-recent", "all").returncode == 0
    assert wt.exists() != removed


@pytest.mark.parametrize("minutes", ["0", "invalid", "-1"])
def test_later_invalid_window_preserves_tree_and_marker(tmp_path, monkeypatch, minutes):
    queue, _, _, wt, config = retain_recent(tmp_path)
    age_worktree(wt)
    age_retry(queue)
    before = retry_path(queue).stat().st_mtime_ns
    monkeypatch.setenv("WORKTREE_KEEP_MINUTES", minutes)
    assert runner(config, "cleanup-recent", "all").returncode != 0
    assert wt.exists()
    assert retry_path(queue).stat().st_mtime_ns == before


def test_later_pass_is_bounded_and_continues_on_next_invocation(tmp_path):
    queue, _, _, _, config = make_repo(tmp_path)
    for index in range(33):
        job_id = f"old-{index:02d}"
        write_text(retry_path(queue, job_id), "")
        age_retry(queue, job_id)
    assert runner(config, "cleanup-recent", "all").returncode == 0
    assert len(list(retry_path(queue).parent.iterdir())) == 1
    assert runner(config, "cleanup-recent", "all").returncode == 0
    assert not list(retry_path(queue).parent.iterdir())


def test_later_find_failure_preserves_tree_and_marker(tmp_path, monkeypatch):
    queue, _, _, wt, config = retain_recent(tmp_path)
    age_worktree(wt)
    age_retry(queue)
    tools = tmp_path / "tools"
    write_text(tools / "find", "#!/usr/bin/env bash\nexit 1\n")
    (tools / "find").chmod(int("755", 8))
    monkeypatch.setenv("PATH", str(tools) + os.pathsep + os.environ["PATH"])
    assert runner(config, "cleanup-recent", "all").returncode != 0
    assert wt.exists() and retry_path(queue).exists()


def test_failed_child_is_backed_off_without_starving_next_job(tmp_path):
    queue, _, _, wt, config = retain_recent(tmp_path)
    age_worktree(wt)
    age_retry(queue)
    before = retry_path(queue).stat().st_mtime_ns
    # An invalid spec exits before the guarded path can record a keep reason.
    write_text(queue / "jobs" / "done.md", "REPO: .invalid\n")
    write_text(retry_path(queue, "next"), "")
    age_retry(queue, "next")
    result = runner(config, "cleanup-recent", "all")
    assert result.returncode == 0
    assert "cleanup retry failed: done" in result.stderr
    assert wt.exists()
    assert retry_path(queue).stat().st_mtime_ns > before
    assert not retry_path(queue, "next").exists()
    again = runner(config, "cleanup-recent", "all")
    assert "retry cleanup" not in again.stdout


@WINDOWS_ONLY
@pytest.mark.parametrize("mode", ["disk-hold", "empty", "dry-run", "paused"])
def test_pump_retries_cleanup_before_admission(tmp_path, mode):
    queue, _, _, wt, config = retain_recent(tmp_path)
    age_worktree(wt)
    age_retry(queue)
    if mode == "paused":
        write_text(queue / "PAUSE", "hold\n")
    # No queue entries: the only executable operation is guarded cleanup.
    command = (f"& '{(SCRIPT_DIR / 'pump.ps1').as_posix()}' "
               f"-ConfigPath '{config.as_posix()}' "
               "-FreeSpaceProbe { param($root,$role) "
               + ("1" if mode == "disk-hold" else "999") + " }")
    if mode == "dry-run":
        command += " -DryRun"
    run(["powershell", "-NoProfile", "-Command", command])
    assert wt.exists() == (mode in ("paused", "dry-run"))
    log = (queue / "pump.log").read_text()
    reason = {"disk-hold": "clone-disk-under-50GB", "empty": "no-queue-file",
              "dry-run": "no-queue-file", "paused": "PAUSE-file"}[mode]
    assert "reason=" + reason in log


def test_pump_wires_guarded_pass_before_disk_admission():
    pump = (SCRIPT_DIR / "pump.ps1").read_text()
    call = pump.index("Invoke-RecentCleanup $ConfigPath")
    assert call < pump.index("$cloneFree = Get-FreeDiskGb")
    assert "cleanup-recent" in pump
    assert "min_free_gb=" not in (SCRIPT_DIR / "limits.txt").read_text()
