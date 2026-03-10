# WRK-1097 AC Test Matrix

| AC | Test | Command | Result | Notes |
|----|------|---------|--------|-------|
| AC1: whats-next UNCLAIMED section | pending + lock age 30min → UNCLAIMED array | `pytest test_unclaimed_detection.py::TestWhatNextSessionLock::test_pending_with_recent_lock_goes_to_unclaimed_active` | PASS | Lock age < 7200s routed to UNCLAIMED_ACTIVE, not HIGH_UNBLOCKED |
| AC1: no false positives (stale) | pending + lock age 3h → HIGH bucket | `pytest test_unclaimed_detection.py::TestWhatNextSessionLock::test_pending_with_stale_lock_goes_to_high_unblocked` | PASS | Stale locks correctly excluded |
| AC1: boundary at exactly 7200s | lock age = 7200s → stale | `pytest test_unclaimed_detection.py::TestWhatNextSessionLock::test_lock_at_exactly_7200s_is_stale_boundary` | PASS | Boundary correctly stale |
| AC1: no lock → normal | pending + no lock → HIGH | `pytest test_unclaimed_detection.py::TestWhatNextSessionLock::test_pending_with_no_lock_goes_to_high_unblocked` | PASS | Items without locks unaffected |
| AC2: active-sessions.sh | pending + recent lock → unclaimed | `pytest test_unclaimed_detection.py::TestActiveSessions::test_pending_item_with_recent_lock_reported_as_unclaimed` | PASS | Queue folder = canonical source |
| AC2: active-sessions.sh claimed | working + recent lock → claimed | `pytest test_unclaimed_detection.py::TestActiveSessions::test_working_item_with_recent_lock_reported_as_claimed` | PASS | |
| AC2: stale lock skipped | lock >2h → not in output | `pytest test_unclaimed_detection.py::TestActiveSessions::test_stale_lock_older_than_2h_is_skipped` | PASS | |
| AC3: start_stage guard | stage 9 + pending → exit(1) | `pytest test_unclaimed_detection.py::TestStartStagePendingGuard::test_stage9_with_item_in_pending_exits_nonzero` | PASS | Error message includes claim-item.sh command |
| AC3: working/ unaffected | stage 9 + working → no exit | `pytest test_unclaimed_detection.py::TestStartStagePendingGuard::test_stage9_with_item_in_working_exits_zero` | PASS | |
| AC3: pre-claim stages unaffected | stage 2 + pending → no exit | `pytest test_unclaimed_detection.py::TestStartStagePendingGuard::test_stage2_with_item_in_pending_exits_zero` | PASS | Guard only for stage ≥9 |
| AC4: existing tests pass | full work-queue test suite | `uv run --no-project python -m pytest scripts/work-queue/tests/ -q` | PASS | 148 passed, 1 pre-existing skip, 0 failures |

## Summary

- **PASS count**: 11
- **FAIL count**: 0
- **Stage 12 gate**: MET (≥3 PASS, 0 FAIL)

## Run Date
2026-03-10
