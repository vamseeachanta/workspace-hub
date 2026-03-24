# Variation Test Results: WRK-663

## Test Suite

### Test 1 — Out-of-Scope Cleanup
- **Command**: `ls .claude/work-queue/pending/WRK-361.md`
- **Expected**: File not found (moved to done).
- **Result**: PASS.

### Test 2 — Index Regeneration
- **Command**: `python3 .claude/work-queue/scripts/generate-index.py`
- **Expected**: "Queue state validation passed."
- **Result**: PASS.

### Test 3 — TOP-10 Identification
- **Command**: `grep -A 10 "Priority TOP-10" specs/wrk/WRK-663/queue-triage-report.md`
- **Expected**: List of 10 items with agents and workstations.
- **Result**: PASS.
