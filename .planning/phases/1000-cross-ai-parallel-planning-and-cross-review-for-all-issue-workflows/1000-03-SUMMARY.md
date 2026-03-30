---
phase: 1000-cross-ai-parallel-planning-and-cross-review-for-all-issue-workflows
plan: 03
subsystem: ai-orchestration
tags: [gsd-skills, parallel-review, cross-plan, workflow-integration, bash-parallel]

# Dependency graph
requires:
  - phase: 1000-01
    provides: "cross_modes section in routing-config.yaml with per-tier flags"
  - phase: 1000-02
    provides: "cross-plan.sh parallel dispatch script"
provides:
  - "Parallel review invocation in review.md with tier-based activation (& + wait)"
  - "Cross-plan mode detection and dispatch in plan-phase.md"
  - "--cross-plan and --tier flags for plan-phase.md"
  - "Fallback to single-planner/sequential modes when cross-plan/review disabled"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Parallel bash dispatch with & + wait + associative array PID tracking in review.md"
    - "Tier-based mode detection reading cross_modes from routing-config.yaml via python3+yaml"
    - "REVIEW_TMPDIR isolation pattern for parallel output collection"
    - "check_cross_plan_mode step pattern: config check -> flag override -> dispatch -> fallback"

key-files:
  created: []
  modified:
    - .codex/get-shit-done/workflows/review.md
    - .gemini/get-shit-done/workflows/review.md
    - .codex/get-shit-done/workflows/plan-phase.md
    - .gemini/get-shit-done/workflows/plan-phase.md

key-decisions:
  - "Modified .codex/ and .gemini/ tracked copies (canonical .claude/ is gitignored, not in worktree)"
  - "Parallel review is default for Route B/C/REASONING; sequential fallback for Route A (SIMPLE)"
  - "Cross-plan mode uses plan_count heuristic for tier detection: 3+ plans = COMPLEX, 1-2 = STANDARD"
  - "CROSS_PLAN_INPUT passed as optional files_to_read entry to planner agent prompt"

patterns-established:
  - "check_cross_plan_mode: tier detection -> config read -> flag override -> dispatch -> fallback pattern"
  - "REVIEW_PIDS associative array pattern for parallel CLI process tracking"
  - "REVIEW_TMPDIR temp directory pattern for isolated parallel output"

requirements-completed: [XSKILL-01, XSKILL-02, XREV-01]

# Metrics
duration: 4min
completed: 2026-03-30
---

# Phase 1000 Plan 03: GSD Skill Integration Summary

**Parallel review invocation (bash & + wait) in review.md and cross-plan mode detection with cross-plan.sh dispatch in plan-phase.md, completing the cross-AI workflow wiring**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-30T11:24:44Z
- **Completed:** 2026-03-30T11:28:27Z
- **Tasks:** 3 (2 auto + 1 checkpoint auto-approved)
- **Files modified:** 4

## Accomplishments
- Replaced sequential CLI invocation with parallel bash & + wait pattern in review.md, with tier-based activation reading cross_modes.cross_review from routing-config.yaml
- Added check_cross_plan_mode step (7.6) to plan-phase.md that reads routing-config.yaml, dispatches cross-plan.sh when enabled, and passes merged output to planner agent
- Added --cross-plan and --tier flags to plan-phase.md argument parsing for manual override
- Both skills gracefully fall back to single-planner/sequential modes when cross-plan/review is disabled or fails

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace sequential review invocation with parallel mode in review.md** - `8bf5dc8a` (feat)
2. **Task 2: Add cross-plan mode detection and dispatch to plan-phase.md** - `7017d991` (feat)
3. **Task 3: Verify cross-plan and parallel review integration** - auto-approved checkpoint

## Files Created/Modified
- `.codex/get-shit-done/workflows/review.md` - Parallel review invocation with REVIEW_PIDS tracking, REVIEW_TMPDIR isolation, tier-based mode detection
- `.gemini/get-shit-done/workflows/review.md` - Same parallel review changes (provider-adapted copy)
- `.codex/get-shit-done/workflows/plan-phase.md` - Cross-plan mode detection (step 7.6), --cross-plan/--tier flags, CROSS_PLAN_INPUT in planner prompt
- `.gemini/get-shit-done/workflows/plan-phase.md` - Same cross-plan changes (provider-adapted copy)

## Decisions Made
- Modified .codex/ and .gemini/ tracked copies since .claude/get-shit-done/ is gitignored and not present in worktrees. The .claude/ version needs separate out-of-band sync.
- Used python3 + yaml for reading routing-config.yaml (consistent with existing patterns, available in project environment)
- Cross-plan step inserted as 7.6 (between Nyquist verification 7.5 and planner spawn 8) to maintain step numbering continuity

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Modified tracked copies instead of gitignored .claude/ path**
- **Found during:** Task 1 (review.md modification)
- **Issue:** Plan referenced .claude/get-shit-done/workflows/ but this directory is gitignored and absent from worktrees. Only .codex/ and .gemini/ copies are git-tracked.
- **Fix:** Modified .codex/ and .gemini/ tracked copies instead. The .claude/ version lives only in the main repo working tree and needs out-of-band sync.
- **Files modified:** .codex/ and .gemini/ versions of review.md and plan-phase.md
- **Verification:** All acceptance criteria verified against tracked copies
- **Committed in:** 8bf5dc8a, 7017d991

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** File path adaptation was necessary for git-tracked files. Functionality identical. The gitignored .claude/ copy should be synced from .codex/ or .gemini/ versions.

## Issues Encountered
None beyond the file path deviation noted above.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all code paths are fully wired with real config reads and script dispatch.

## Next Phase Readiness
- Phase 1000 is now complete: config (Plan 01) + script (Plan 02) + skill integration (Plan 03)
- The cross-plan and parallel review infrastructure is wired end-to-end
- The .claude/ gitignored copies need manual sync from tracked versions
- Ready for real-world testing: `--cross-plan` flag on plan-phase, parallel reviews on any phase

## Self-Check: PASSED

All 5 files verified present. Both task commits (8bf5dc8a, 7017d991) found in git log.

---
*Phase: 1000-cross-ai-parallel-planning-and-cross-review-for-all-issue-workflows*
*Completed: 2026-03-30*
