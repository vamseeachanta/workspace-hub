# WRK-1123 Plan Review — Final

## Plan Summary
Route A (simple). Three changes to `start_stage.py`:
1. `_maybe_purge_stale_lock()` — auto-purge stale session-lock (PID dead + age > 2h)
2. `_stage1_working_guard()` — exits 1 if item not in working/ at Stage 1
3. `test_start_stage_guards.py` — 7 unit tests

## Confirmation

decision: passed
confirmed_by: vamsee
confirmed_at: 2026-03-11T11:45:00Z
notes: Route A plan approved. Inline implementation — no new deps, stdlib only.
