confirmed_by: vamsee
confirmed_at: 2026-03-12T10:48:37Z
decision: passed

# WRK-1138 Plan — Final Review

Route A inline plan — approved at Stage 1 scope review.

## Plan Steps
1. Add `is_archived` guard in `whats-next.sh` `process_file()` — 3-line change
2. Add early-exit in `claim-item.sh` before Stage 5 check — 5-line change
3. Create `scripts/work-queue/scan-ghost-pending.sh` (detect + `--fix` mode)
4. Write `tests/unit/test_ghost_pending.sh`

All steps completed. 12/12 tests pass.
