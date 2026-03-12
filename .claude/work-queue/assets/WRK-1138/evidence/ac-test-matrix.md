# WRK-1138 AC Test Matrix

| # | Acceptance Criterion | Status | Evidence |
|---|---------------------|--------|----------|
| 1 | `archive-item.sh` sweeps all queue dirs | PASS | test_ghost_pending.sh: sweep tests 10-12 |
| 2 | `whats-next.sh` skips archived pending items | PASS | is_archived() guard at line 175; test 1-3 |
| 3 | `claim-item.sh` early-exits with "already archived" | PASS | line 52; test 6-7 |
| 4 | `scan-ghost-pending.sh` detect + --fix mode | PASS | script exists, executable; test 1-5, 8 |
| 5 | Tests pass 9+/9 | PASS | 12/12 PASS |
| 6 | Live queue returns 0 ghosts | PASS | `scan-ghost-pending.sh` → "✔ No ghost pending items found." |

**Result: 6/6 PASS**

## Test run output
```
Results: 12 PASS, 0 FAIL
```
## Live scan
```
✔ No ghost pending items found.
```
