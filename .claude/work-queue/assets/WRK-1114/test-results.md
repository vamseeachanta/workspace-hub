# WRK-1114 Test Results

**Test Suite:** `tests/work-queue/test-machine-id-ranges.sh`
**Run date:** 2026-03-10
**Result:** 5 PASS, 0 FAIL

## Test Cases

| # | Scenario | Expected | Actual | Status |
|---|----------|----------|--------|--------|
| 1 | dev-primary empty queue | ID 001 | 001 | PASS |
| 2 | licensed-win-1 empty queue (floor=5000) | ID 5000 | 5000 | PASS |
| 3 | dev-primary with MAX_ID=1113 | ID 1114 | 1114 | PASS |
| 4 | licensed-win-1 with MAX_ID=5001 | ID 5002 | 5002 | PASS |
| 5 | dev-primary ceiling < licensed-win-1 floor | Non-overlapping | 4999 < 5000 | PASS |
