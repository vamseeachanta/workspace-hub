# WRK-1135 Plan — Route A

## Scope
Fix whats-next.sh to handle coordinating feature WRKs.

## Steps
1. Detect `type: feature` + `status: coordinating` in `process_file()`
2. Count child progress (archived/total) and redirect to COORDINATING_ITEMS
3. Render `◈ COORDINATING` section before `▶ WORKING`
4. Add 3 bats tests covering all 3 ACs

## Files
- scripts/work-queue/whats-next.sh
- tests/work-queue/test_whats_next.bats

---
confirmed_by: vamsee
confirmed_at: 2026-03-11T16:05:00Z
decision: passed
