# WRK-1114 Test Results

**Test Suite:** `tests/work-queue/test-machine-id-ranges.sh`
**Run date:** 2026-03-10
**Result:** 5 PASS, 0 FAIL

## Test Cases

| # | Scenario | Expected | Actual | Status |
|---|----------|----------|--------|--------|
| 1 | ace-linux-1 empty queue | ID 001 | 001 | PASS |
| 2 | acma-ansys05 empty queue (floor=5000) | ID 5000 | 5000 | PASS |
| 3 | ace-linux-1 with MAX_ID=1113 | ID 1114 | 1114 | PASS |
| 4 | acma-ansys05 with MAX_ID=5001 | ID 5002 | 5002 | PASS |
| 5 | ace-linux-1 ceiling < acma-ansys05 floor | Non-overlapping | 4999 < 5000 | PASS |
