---
phase: 01-accelerate-digitalmodel-development
plan: 03
subsystem: structural-analysis
tags: [asme-b31-4, wall-thickness, barlow, pipeline, code-strategy, tdd]

# Dependency graph
requires: []
provides:
  - "ASME B31.4 CodeStrategy registered in CODE_REGISTRY"
  - "Burst/collapse/propagation checks for liquid pipelines"
  - "manifest.yaml traceability for ASME B31.4 clauses"
affects: [wall-thickness-analyzer, pipeline-design-reports]

# Tech tracking
tech-stack:
  added: []
  patterns: ["CodeStrategy Protocol + @register_code for new design codes"]

key-files:
  created:
    - digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/asme_b31_4.py
    - digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/manifest.yaml
    - digitalmodel/tests/structural/analysis/wall_thickness_codes/__init__.py
    - digitalmodel/tests/structural/analysis/wall_thickness_codes/conftest.py
    - digitalmodel/tests/structural/analysis/wall_thickness_codes/test_asme_b31_4.py
  modified:
    - digitalmodel/src/digitalmodel/structural/analysis/wall_thickness.py
    - digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/__init__.py

key-decisions:
  - "Burst check uses effective thickness (t - corrosion_allowance) per ASME B31.4 S403.2.1"
  - "Zero effective thickness returns inf utilisation rather than raising exception"
  - "Collapse and propagation use nominal wall thickness consistent with B31.8 pattern"

patterns-established:
  - "TDD RED/GREEN for new CodeStrategy modules"

requirements-completed: [ROADMAP-01-NEWMODULES, D-01, D-02, D-03, D-05, D-06, D-07, D-08]

# Metrics
duration: 11min
completed: 2026-03-25
---

# Phase 01 Plan 03: ASME B31.4 Wall Thickness Code Strategy Summary

**ASME B31.4 liquid pipeline code strategy with Barlow burst (F=0.72), elastic-plastic collapse, and Battelle/AGA propagation checks**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-25T23:05:08Z
- **Completed:** 2026-03-25T23:16:49Z
- **Tasks:** 2 (TDD RED + GREEN)
- **Files modified:** 7

## Accomplishments
- ASME B31.4 registered as 8th code in CODE_REGISTRY via @register_code decorator
- Burst check implements Barlow formula with F=0.72, E=1.0, T=1.0 per S403.2.1
- Collapse uses elastic-plastic transition formula per S403.2.2
- Propagation uses Battelle/AGA p_pr = 24*SMYS*(t/D)^2.4 per S403.2.3
- 7 self-contained tests covering burst, collapse, propagation, and registry
- manifest.yaml maps every function to its ASME B31.4 clause

## Task Commits

Each task was committed atomically:

1. **RED: Failing tests + enum member** - `f0971a36` (test)
2. **GREEN: Implementation + __init__ + manifest** - `a8867170` (feat)

_No REFACTOR commit needed -- style already consistent with B31.8 implementation._

## Files Created/Modified
- `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness.py` - Added ASME_B31_4 to DesignCode enum
- `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/asme_b31_4.py` - Full AsmeB314Strategy implementation (195 lines)
- `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/__init__.py` - Import for auto-registration
- `digitalmodel/src/digitalmodel/structural/analysis/wall_thickness_codes/manifest.yaml` - Clause traceability
- `digitalmodel/tests/structural/analysis/wall_thickness_codes/__init__.py` - Test package init
- `digitalmodel/tests/structural/analysis/wall_thickness_codes/conftest.py` - Self-contained conftest
- `digitalmodel/tests/structural/analysis/wall_thickness_codes/test_asme_b31_4.py` - 7 tests across 4 classes

## Decisions Made
- Burst check uses effective thickness (t - corrosion_allowance) per ASME B31.4 S403.2.1, unlike B31.8 which uses nominal thickness
- Zero effective thickness returns inf utilisation rather than raising ValueError, consistent with existing code patterns
- Collapse and propagation checks use nominal wall thickness, matching B31.8 convention

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ASME B31.4 code strategy fully operational and registered
- WallThicknessAnalyzer can now dispatch to AsmeB314Strategy
- Ready for plans 04-05 in wave 2

## Self-Check: PASSED

- All 6 files found on disk
- Both commit hashes (f0971a36, a8867170) verified in git log
- asme_b31_4.py: 198 lines (min 100)
- test_asme_b31_4.py: 197 lines (min 80)
- manifest.yaml: present
- All 7 tests pass
- DesignCode.ASME_B31_4 in CODE_REGISTRY confirmed

---
*Phase: 01-accelerate-digitalmodel-development*
*Completed: 2026-03-25*
