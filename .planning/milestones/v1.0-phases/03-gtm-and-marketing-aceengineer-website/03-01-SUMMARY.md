---
phase: 03-gtm-and-marketing-aceengineer-website
plan: 01
subsystem: calculators
tags: [javascript, tdd, dnv-rp-f109, asme-b31.4, jest, engineering-calculators]

# Dependency graph
requires:
  - phase: 01-accelerate-digitalmodel-development
    provides: YAML manifests with function signatures for OBS and wall thickness modules
provides:
  - OBS calculator engine (obs-calculator-engine.js) with 5 exported functions
  - Wall thickness engine (wall-thickness-engine.js) with 4 exported functions
  - 19 passing unit tests covering both engines
  - Jest project entries for obs-calculator and wall-thickness
affects: [03-02, 03-03]

# Tech tracking
tech-stack:
  added: []
  patterns: [pure-function-engine-pattern, commonjs-conditional-export, tdd-red-green]

key-files:
  created:
    - aceengineer-website/assets/js/obs-calculator-engine.js
    - aceengineer-website/assets/js/wall-thickness-engine.js
    - aceengineer-website/tests/js/obs-calculator.test.js
    - aceengineer-website/tests/js/wall-thickness.test.js
  modified:
    - aceengineer-website/package.json

key-decisions:
  - "Followed NPV engine pattern exactly: 'use strict', JSDoc, pure functions, conditional CommonJS export"
  - "Used var instead of const/let for maximum browser compatibility (matching existing NPV engine)"
  - "collapseCheck defaults E=207000 MPa and nu=0.3 when not provided for API simplicity"

patterns-established:
  - "Engineering calculator engine: pure JS, no DOM, conditional CommonJS export, comprehensive JSDoc with standard references"
  - "TDD for calculator engines: hand-calculated expected values in test comments for traceability"

requirements-completed: [D-01, D-02]

# Metrics
duration: 10min
completed: 2026-03-26
---

# Phase 03 Plan 01: Calculator Engines Summary

**TDD-driven OBS (DNV-RP-F109) and wall thickness (ASME B31.4 + Timoshenko) JavaScript calculation engines with 19 passing tests**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-26T21:38:20Z
- **Completed:** 2026-03-26T21:48:00Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- On-bottom stability engine with 5 functions: hydrodynamic force, lift force, submerged weight, absolute stability check, pipeline convenience function
- Wall thickness engine with 4 functions: burst check (Barlow), collapse check (Timoshenko), minimum wall thickness, pipeline convenience function
- 19 new tests all passing with hand-calculated expected values traceable to engineering standards
- Full test suite (118 tests across 6 projects) remains green

## Task Commits

Each task was committed atomically (TDD RED/GREEN):

1. **Task 1: On-bottom stability engine with TDD**
   - `00dd33b` (test) RED: failing tests for OBS calculator engine
   - `e6bf2e1` (feat) GREEN: implement OBS calculator engine
2. **Task 2: Wall thickness engine with TDD**
   - `4925f38` (test) RED: failing tests for wall thickness engine
   - `8ce5e93` (feat) GREEN: implement wall thickness engine

_Note: All commits in aceengineer-website repo (separate from workspace-hub)_

## Files Created/Modified
- `aceengineer-website/assets/js/obs-calculator-engine.js` - OBS calculator: hydrodynamic/lift forces, submerged weight, stability check per DNV-RP-F109
- `aceengineer-website/assets/js/wall-thickness-engine.js` - Wall thickness: burst/collapse checks, min thickness per ASME B31.4 + Timoshenko
- `aceengineer-website/tests/js/obs-calculator.test.js` - 11 unit tests for OBS engine with hand-calculated values
- `aceengineer-website/tests/js/wall-thickness.test.js` - 8 unit tests for wall thickness engine with hand-calculated values
- `aceengineer-website/package.json` - Added obs-calculator and wall-thickness Jest project entries

## Decisions Made
- Followed NPV engine pattern exactly: `'use strict'`, JSDoc with standard references, pure functions, conditional CommonJS export at bottom
- Used `var` instead of `const/let` matching the existing NPV engine for maximum browser compatibility
- collapseCheck defaults Young's modulus (207000 MPa) and Poisson's ratio (0.3) for steel when not provided, simplifying API while remaining explicit in documentation
- obsPipeline and wallThicknessPipeline convenience functions accept params objects mapping to YAML manifest inputs per D-02

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- Jest 30.x uses `--testPathPatterns` (plural) instead of `--testPathPattern` (singular). Adjusted test commands accordingly. No impact on test results.

## Known Stubs

None - both engines are fully functional with all exported functions wired to calculations.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Both engines are ready for HTML page integration (Plan 03-02/03-03)
- Engines importable via `require()` for tests and via `<script src>` for browser
- All 13 OBS inputs and 7 wall thickness inputs map directly to YAML manifest function signatures

## Self-Check: PASSED

- All 5 files exist on disk
- All 4 commits verified in git history (00dd33b, e6bf2e1, 4925f38, 8ce5e93)
- Full test suite: 118/118 passing

---
*Phase: 03-gtm-and-marketing-aceengineer-website*
*Completed: 2026-03-26*
