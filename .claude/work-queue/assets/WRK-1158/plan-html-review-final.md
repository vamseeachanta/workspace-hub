# WRK-1158 Plan Final Review

## Plan: check-gates-green.sh

- Script `scripts/work-queue/check-gates-green.sh WRK-NNN` (~35 lines)
- Calls `verify-gate-evidence.py $WRK_ID` close phase; propagates exit 2 (infra failure)
- Counts `: OK `, `: WARN `, `: MISSING ` lines in stdout
- If MISSING > 0 → list missing gates + exit 1; else print summary + exit 0
- TDD: 3 bash tests (all-OK, MISSING-present, WARN-only)
- Integration: stage-17-user-review-implementation.yaml + close-item.sh comment

## Confirmation

confirmed_by: vamsee
confirmed_at: 2026-03-12T10:45:00Z
decision: passed
