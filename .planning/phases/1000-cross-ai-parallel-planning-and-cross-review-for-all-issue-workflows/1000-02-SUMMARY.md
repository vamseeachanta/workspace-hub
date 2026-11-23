---
phase: 1000-cross-ai-parallel-planning-and-cross-review-for-all-issue-workflows
plan: 02
subsystem: ai-orchestration
tags: [bash, parallel-dispatch, plan-merge, cross-ai, structured-diff]

# Dependency graph
requires:
  - phase: none
    provides: "First plan in phase; uses existing cross-review-loop.sh patterns"
provides:
  - "cross-plan.sh: parallel 3-CLI plan dispatch, section extraction, and merge"
  - "--dry-run mode for testing without live API calls"
  - "Structured diff pre-filtering (auto-merge agreed, synthesize divergent)"
affects: [1000-01, 1000-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Parallel bash dispatch with & + wait + PID tracking for multi-AI orchestration"
    - "GNU sed single-line XML tag extraction with grep pre-check"
    - "Arithmetic safety: ((count++)) || true under set -e"

key-files:
  created:
    - "scripts/development/ai-plan/cross-plan.sh"
  modified: []

key-decisions:
  - "Used grep pre-check for single-line XML tags to avoid GNU sed range bug where start+end on same line does not close range"
  - "DRY_RUN mode assumes all 3 providers available (mocks CLI calls) so testing works without live CLIs"
  - "Claude selected as synthesis agent for divergent sections per D-03 architecture decision"
  - "Fallback to full-plan synthesis when structured extraction fails for 2+ providers"

patterns-established:
  - "ai-plan directory: scripts/development/ai-plan/ for planning orchestration scripts"
  - "Provider dispatch pattern: dispatch_plan() function with case statement per CLI"
  - "Section extraction: extract_section() with single-line and multi-line handling"

requirements-completed: [XPLAN-01, XPLAN-02, XPLAN-03]

# Metrics
duration: 7min
completed: 2026-03-30
---

# Phase 1000 Plan 02: Cross-Plan Script Summary

**Parallel 3-CLI plan dispatch with structured diff merge (auto-merge agreed sections, LLM synthesis for divergent) in 720-line bash script**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-30T03:57:12Z
- **Completed:** 2026-03-30T04:03:59Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Created `scripts/development/ai-plan/cross-plan.sh` (720 lines) implementing D-03, D-04, D-05, D-11
- Parallel dispatch to Claude, Codex, Gemini via bash `&` + `wait` with PID tracking
- Structured diff: section extraction for objective/tasks/verification/success_criteria, auto-merge agreed, synthesis prompt for divergent
- Full --dry-run mode that exercises dispatch, extraction, comparison, and merge without live API calls
- Handles partial failures (2-of-3 minimum), Codex NO_OUTPUT (< 50 bytes threshold), malformed output fallback
- Cleanup trap prevents /tmp pollution

## Task Commits

Each task was committed atomically:

1. **Task 1: Create cross-plan.sh with parallel dispatch, section extraction, and merge** - `fde314c4` (feat)
2. **Task 2: Verify cross-plan.sh with dry-run end-to-end test** - `911277e7` (fix)

## Files Created/Modified
- `scripts/development/ai-plan/cross-plan.sh` - Parallel multi-AI plan generation and merge script (720 lines, executable)

## Decisions Made
- **GNU sed range bug workaround:** When `<tag>content</tag>` appears on a single line, GNU sed's range `/<tag>/,/<\/tag>/p` does not close properly (treats same-line end as range start only). Fixed with grep pre-check for single-line tags before falling back to sed range for multi-line.
- **DRY_RUN CLI bypass:** In dry-run mode, all 3 providers are assumed available and CLI calls are replaced with file copies. This ensures the full pipeline (dispatch, extraction, comparison, merge) is exercised without network dependencies.
- **Arithmetic safety:** All `((count++))` expressions use `|| true` suffix to prevent `set -e` from exiting when incrementing from 0 (bash arithmetic returns exit code 1 for expression value 0).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed ((count++)) causing exit under set -e**
- **Found during:** Task 2 (dry-run testing)
- **Issue:** Bash `((count++))` returns exit code 1 when count is 0 (expression evaluates to 0 before increment), causing `set -e` to terminate the script
- **Fix:** Added `|| true` to all 6 arithmetic increment expressions
- **Files modified:** scripts/development/ai-plan/cross-plan.sh
- **Verification:** Dry-run completes with exit code 0
- **Committed in:** 911277e7

**2. [Rule 1 - Bug] Fixed log_verbose failing under set -e**
- **Found during:** Task 2 (dry-run testing)
- **Issue:** `[[ "$VERBOSE" == "true" ]] && echo ...` returns false when VERBOSE is false, triggering set -e
- **Fix:** Added `|| true` to the log_verbose function
- **Files modified:** scripts/development/ai-plan/cross-plan.sh
- **Verification:** Script runs cleanly without --verbose flag
- **Committed in:** 911277e7

**3. [Rule 1 - Bug] Fixed extract_section for single-line XML tags**
- **Found during:** Task 2 (dry-run testing)
- **Issue:** GNU sed range `/<tag>/,/<\/tag>/p` does not close when both patterns match the same line, causing extraction to run to end of file
- **Fix:** Added grep pre-check for single-line form before using sed range for multi-line
- **Files modified:** scripts/development/ai-plan/cross-plan.sh
- **Verification:** Both single-line and multi-line tags extract correctly in dry-run
- **Committed in:** 911277e7

**4. [Rule 3 - Blocking] DRY_RUN mode requires CLI detection bypass**
- **Found during:** Task 2 (dry-run testing)
- **Issue:** detect_clis() requires claude/codex/gemini executables on PATH, but dry-run should work without them
- **Fix:** Added early return in detect_clis() when DRY_RUN=true, assuming all 3 providers available
- **Files modified:** scripts/development/ai-plan/cross-plan.sh
- **Verification:** Dry-run passes without any CLI installed
- **Committed in:** 911277e7

---

**Total deviations:** 4 auto-fixed (3 bugs, 1 blocking)
**Impact on plan:** All fixes necessary for dry-run correctness. No scope creep. All bugs discovered and fixed during Task 2 verification as expected.

## Issues Encountered
None beyond the auto-fixed bugs above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- cross-plan.sh is ready for integration into GSD plan-phase.md workflow (Plan 01 scope)
- routing-config.yaml cross_modes integration ready (Plan 01 scope)
- Live testing with actual CLIs (claude, codex, gemini) recommended before production use

## Self-Check: PASSED

- scripts/development/ai-plan/cross-plan.sh: FOUND (720 lines, executable)
- 1000-02-SUMMARY.md: FOUND
- Commit fde314c4: FOUND
- Commit 911277e7: FOUND

---
*Phase: 1000-cross-ai-parallel-planning-and-cross-review-for-all-issue-workflows*
*Completed: 2026-03-30*
