# WRK-1049 Test Summary

## Acceptance Criteria Results

| # | AC | Status |
|---|-----|--------|
| AC1 | process.md Step 4 is script-first redirect (no bash mv logic) | PASS |
| AC2 | WRK item can never exist in both pending/ and working/ after claim-item.sh | PASS |
| AC3 | Concurrent claim: second exits 1 (working/ check or mv failure) | PASS |
| AC4 | session-lock.yaml written at Stage 1; updated to status=claimed on successful claim | PASS |
| AC5 | active-wrk mismatch logs warning when existing working/ item detected | PASS |
| AC6 | T1–T5 all pass | PASS |

## Test Results

### test-claim-collision.sh (7/7 pass)
- T1: collision guard — item already in working/ → exit 1 ✓
- T2: start_stage.py Stage 1 writes session-lock.yaml ✓
- T3a: session_pid present in lock ✓
- T3b: hostname present in lock ✓
- T3c: locked_at present in lock ✓
- T4: collision message includes lock details (hostname/pid) ✓
- T5: atomic mv race — exactly one mover wins ✓

### Full suite (scripts/work-queue/tests/)
- 115 pass, 1 pre-existing failure (T41 skill line count — unrelated)
