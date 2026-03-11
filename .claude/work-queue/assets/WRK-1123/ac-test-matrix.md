# WRK-1123 AC Test Matrix

| AC | Test | Status |
|----|------|--------|
| Stage 1 on pending item → exits 1 | test_stage1_guard_blocks_pending | PASS |
| Stage 1 on working item → proceeds | test_stage1_guard_passes_working | PASS |
| Working dir exists but item absent → exits 1 | test_stage1_guard_blocks_when_working_dir_empty | PASS |
| Stale lock (dead PID + age>2h) purged | test_purge_stale_lock_removes_dead_pid_old_lock | PASS |
| Recent lock (<2h) not purged | test_purge_stale_lock_keeps_recent_lock | PASS |
| Live PID lock not purged | test_purge_stale_lock_keeps_live_pid | PASS |
| No-op when lock absent | test_purge_stale_lock_noop_when_absent | PASS |

Run: `uv run --no-project python -m pytest scripts/work-queue/tests/test_start_stage_guards.py -v`
Result: **7 passed**
