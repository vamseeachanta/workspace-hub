# WRK-5140 Cross-Review Package

## Mission
Remove deprecated `next-id.sh` and enforce `gh-next-id.sh` for all WRK ID allocation. Add deterministic collision avoidance via static blocklist.

## Plan Summary (8 tasks)
1. **Task 1a:** Generate static blocklist of 1,155 existing WRK IDs + generator script
2. **Task 1b:** Add blocklist check + auto-burn loop to `gh-next-id.sh` (checks blocklist via grep, falls back to live queue scan, burns colliding GH issues and retries up to 200x)
3. **Task 2:** Replace `next-id.sh` with hard-error stub (exit 1 + message pointing to gh-next-id.sh)
4. **Tasks 3-5:** Migrate 3 bash callers (new-feature.sh, create-spinoff-wrk.sh, dep-health.sh)
5. **Task 6:** Migrate 2 Python callers (release_scan_wrk.py, comprehensive_learning_pipeline.py)
6. **Task 7:** Update config/state comments to mark machine ranges and last_id as legacy

## Key Design Decisions
- **Static blocklist + live scan** (not just live scan): survives file deletion, fast grep lookup
- **Auto-burn** (not warning): deterministic — no human intervention needed for the ~42 imminent collisions
- **Append-on-allocate**: new IDs auto-added to blocklist keeping it current
- **200 retry cap**: covers all 177 known collision candidates with headroom

## Number Analysis
- 1,155 existing local WRK IDs (range 1-6670)
- 177 future collision candidates: 42 in 1332-1392 (imminent), 135 in 5000-5140 (years away)
- 0 IDs in 1393-4999 gap (safe landing zone)

## Review Questions
1. Is the auto-burn approach appropriate for handling ~42 imminent collisions?
2. Is the blocklist + live scan dual-layer sufficient for permanence?
3. Any risks with the hard-error stub approach for next-id.sh?

## Full Plan
See: `specs/wrk/WRK-5140/plan.md`
GH Issue: https://github.com/vamseeachanta/workspace-hub/issues/1330
