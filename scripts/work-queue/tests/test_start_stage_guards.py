"""
test_start_stage_guards.py — WRK-1123 AC verification.

Tests _stage1_working_guard() and _maybe_purge_stale_lock() in isolation.

Run with:
  uv run --no-project python -m pytest scripts/work-queue/tests/test_start_stage_guards.py -v
"""
import datetime
import os
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

from start_stage import _maybe_purge_stale_lock, _stage1_working_guard


# ── _stage1_working_guard ─────────────────────────────────────────────────────

def test_stage1_guard_blocks_pending(tmp_path):
    """Stage 1 on a pending item exits 1."""
    queue = tmp_path / "work-queue"
    (queue / "pending").mkdir(parents=True)
    (queue / "working").mkdir()
    (queue / "pending" / "WRK-999.md").write_text("id: WRK-999\n")
    with pytest.raises(SystemExit) as exc_info:
        _stage1_working_guard("WRK-999", str(queue))
    assert exc_info.value.code == 1


def test_stage1_guard_passes_working(tmp_path):
    """Stage 1 on a working item does not exit."""
    queue = tmp_path / "work-queue"
    (queue / "working").mkdir(parents=True)
    (queue / "working" / "WRK-999.md").write_text("id: WRK-999\n")
    _stage1_working_guard("WRK-999", str(queue))  # must not raise


def test_stage1_guard_blocks_when_working_dir_empty(tmp_path):
    """Stage 1 exits 1 when working/ exists but item file is absent."""
    queue = tmp_path / "work-queue"
    (queue / "working").mkdir(parents=True)
    with pytest.raises(SystemExit) as exc_info:
        _stage1_working_guard("WRK-999", str(queue))
    assert exc_info.value.code == 1


# ── _maybe_purge_stale_lock ───────────────────────────────────────────────────

def _write_lock(path: pathlib.Path, pid: int, age_seconds: int) -> None:
    locked_at = datetime.datetime.utcnow() - datetime.timedelta(seconds=age_seconds)
    path.write_text(
        f"wrk_id: WRK-999\n"
        f"session_pid: {pid}\n"
        f"locked_at: \"{locked_at.strftime('%Y-%m-%dT%H:%M:%SZ')}\"\n"
        f"status: in_progress\n"
    )


def test_purge_stale_lock_removes_dead_pid_old_lock(tmp_path):
    """Lock with dead PID and age > 2h is removed."""
    lock = tmp_path / "session-lock.yaml"
    _write_lock(lock, pid=999999999, age_seconds=9000)  # ~2.5h, PID surely dead
    _maybe_purge_stale_lock(lock)
    assert not lock.exists()


def test_purge_stale_lock_keeps_recent_lock(tmp_path):
    """Lock younger than 2h is not removed even if PID is dead."""
    lock = tmp_path / "session-lock.yaml"
    _write_lock(lock, pid=999999999, age_seconds=3600)  # 1h, under threshold
    _maybe_purge_stale_lock(lock)
    assert lock.exists()


def test_purge_stale_lock_keeps_live_pid(tmp_path):
    """Lock with live PID (current process) is not removed even if old."""
    lock = tmp_path / "session-lock.yaml"
    _write_lock(lock, pid=os.getpid(), age_seconds=9000)
    _maybe_purge_stale_lock(lock)
    assert lock.exists()


def test_purge_stale_lock_noop_when_absent(tmp_path):
    """No error when lock file does not exist."""
    lock = tmp_path / "session-lock.yaml"
    _maybe_purge_stale_lock(lock)  # must not raise
