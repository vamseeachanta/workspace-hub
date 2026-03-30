---
phase: 07-solver-verification-gate
plan: 01
subsystem: infra
tags: [orcfxapi, pytest, solver-boundary, diffraction, git-mv]

# Dependency graph
requires: []
provides:
  - "solver/ subpackage enforcing clean OrcFxAPI import boundary"
  - "@pytest.mark.solver marker for CI test deselection"
  - "Solver fixture directory with skip-if-missing pattern"
  - "Module boundary test validating license-free imports"
affects: [07-02, 07-03]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "solver/ subpackage with top-level import OrcFxAPI (no try/except)"
    - "pytest skip-if-missing fixture pattern for cross-machine artifacts"
    - "Conditional try/except bridge imports in license-free modules"

key-files:
  created:
    - "digitalmodel/src/digitalmodel/hydrodynamics/diffraction/solver/__init__.py"
    - "digitalmodel/src/digitalmodel/hydrodynamics/diffraction/solver/orcawave_converter.py"
    - "digitalmodel/src/digitalmodel/hydrodynamics/diffraction/solver/orcawave_data_extraction.py"
    - "digitalmodel/src/digitalmodel/hydrodynamics/diffraction/solver/report_extractors.py"
    - "digitalmodel/tests/hydrodynamics/diffraction/test_module_boundary.py"
    - "digitalmodel/tests/hydrodynamics/diffraction/test_solver_fixtures.py"
    - "digitalmodel/tests/fixtures/solver/.gitkeep"
  modified:
    - "digitalmodel/src/digitalmodel/hydrodynamics/diffraction/__init__.py"
    - "digitalmodel/src/digitalmodel/hydrodynamics/diffraction/result_extractor.py"
    - "digitalmodel/src/digitalmodel/hydrodynamics/diffraction/report_generator.py"
    - "digitalmodel/src/digitalmodel/hydrodynamics/diffraction/batch_processor.py"
    - "digitalmodel/src/digitalmodel/orcawave/reporting/builder.py"
    - "digitalmodel/pyproject.toml"
    - "digitalmodel/pytest.ini"
    - "digitalmodel/.gitattributes"

key-decisions:
  - "solver/__init__.py uses bare import OrcFxAPI (not try/except) per D-12"
  - "report_generator.py wraps solver.report_extractors import in try/except since it is a shim that must remain importable on license-free machines"
  - "wamit_reference_loader.py and orcawave_runner.py retain method-level OrcFxAPI imports (justified runtime checks)"
  - "pytest.ini updated alongside pyproject.toml since pytest.ini takes precedence"

patterns-established:
  - "solver/ subpackage: all OrcFxAPI-dependent code lives exclusively here"
  - "Bridge pattern: license-free modules import from solver via try/except with AVAILABLE flags"
  - "Fixture skip-if-missing: pytest.skip() in fixture body when artifact not committed"

requirements-completed: [INFRA-01]

# Metrics
duration: 21min
completed: 2026-03-30
---

# Phase 07 Plan 01: Solver Subpackage and Test Infrastructure Summary

**Clean OrcFxAPI license boundary via solver/ subpackage, pytest solver marker, and parametrized module boundary tests**

## Performance

- **Duration:** 21 min
- **Started:** 2026-03-30T21:28:02Z
- **Completed:** 2026-03-30T21:49:20Z
- **Tasks:** 2/2
- **Files modified:** 15

## Accomplishments
- Moved 3 OrcFxAPI-dependent files into diffraction/solver/ subpackage with git mv for history preservation
- All 10 license-free diffraction modules import cleanly on Linux without OrcFxAPI
- Parametrized boundary test validates each license-free module import automatically
- Solver fixture directory ready for Plan 03 artifacts with skip-if-missing pattern

## Task Commits

Each task was committed atomically:

1. **Task 1: Create solver/ subpackage and move OrcFxAPI-dependent files** - `2c429497` (refactor)
2. **Task 2: Add pytest solver marker, fixture directory, and boundary tests** - `0d21f097` (feat)

## Files Created/Modified
- `solver/__init__.py` - Clean import boundary with top-level import OrcFxAPI
- `solver/orcawave_converter.py` - Moved from parent, removed try/except
- `solver/orcawave_data_extraction.py` - Moved from parent, removed try/except
- `solver/report_extractors.py` - Moved from parent, top-level OrcFxAPI import
- `test_module_boundary.py` - 13 tests: parametrized import validation, path verification, marker check
- `test_solver_fixtures.py` - 4 tests: fixture infrastructure and solver marker deselection
- `conftest.py` - Added SOLVER_FIXTURES_DIR and l00/l01 .owr/.xlsx fixtures with skip-if-missing
- `__init__.py` - Updated imports to use solver subpackage paths
- `result_extractor.py` - Import from solver subpackage
- `report_generator.py` - Conditional import from solver.report_extractors
- `batch_processor.py` - Import OrcaWaveConverter from solver
- `builder.py` - Import OrcFxAPI from solver subpackage
- `pyproject.toml` - Added solver marker
- `pytest.ini` - Added solver marker
- `.gitattributes` - Added *.owr binary handling

## Decisions Made
- **solver/__init__.py bare import:** Uses `import OrcFxAPI` without try/except, per D-12. The subpackage fails cleanly if OrcFxAPI unavailable -- consumers use try/except at the import site.
- **report_generator.py conditional import:** This shim re-exports from report_extractors which is now in solver/. Wrapped in try/except so the shim itself remains importable on license-free machines. Without this, test_report_generator.py would fail at collection.
- **pytest.ini dual registration:** The solver marker was added to both pyproject.toml and pytest.ini because pytest.ini takes precedence as the active config. Strict-markers mode would reject @pytest.mark.solver without registration.
- **wamit/runner kept in parent:** Method-level OrcFxAPI imports in wamit_reference_loader.py and orcawave_runner.py are justified runtime availability checks, not structural dependencies.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Wrapped report_generator.py solver import in try/except**
- **Found during:** Task 2 (full diffraction test suite verification)
- **Issue:** report_generator.py imported from solver.report_extractors at top level. Because Python loads solver/__init__.py (which has bare import OrcFxAPI) when importing any submodule, this caused test_report_generator.py to fail at collection on Linux.
- **Fix:** Wrapped the import in try/except with None fallbacks, matching the bridge pattern used elsewhere.
- **Files modified:** report_generator.py
- **Verification:** Full diffraction test suite passes (632 passed, 11 pre-existing failures unrelated to changes)
- **Committed in:** 0d21f097 (Task 2 commit)

**2. [Rule 3 - Blocking] Added solver marker to pytest.ini (not just pyproject.toml)**
- **Found during:** Task 2 (first test run)
- **Issue:** pytest.ini takes precedence over pyproject.toml for config. The solver marker registered only in pyproject.toml was not found by pytest, causing collection error with --strict-markers.
- **Fix:** Added solver marker definition to pytest.ini markers section.
- **Files modified:** pytest.ini
- **Verification:** pytest --markers shows solver marker; all boundary tests pass
- **Committed in:** 0d21f097 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Both fixes necessary for test suite to run. No scope creep.

## Issues Encountered
- 11 pre-existing test failures in diffraction suite (benchmark_runner, unit_box_benchmark, aqwa_backend, cli_integration) confirmed as unrelated to changes by running same tests against stashed (pre-change) codebase.

## Known Stubs
None - all code is functional, no placeholder data.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- solver/ subpackage ready for Plans 02 and 03
- tests/fixtures/solver/ directory ready to receive .owr/.xlsx artifacts from licensed-win-1 (Plan 03)
- @pytest.mark.solver marker ready for Plan 02 test authoring
- Module boundary test will catch any future leakage of OrcFxAPI imports into license-free code

## Self-Check: PASSED

- All 8 created files verified present on disk
- Commit 2c429497 (Task 1) verified in git log
- Commit 0d21f097 (Task 2) verified in git log

---
*Phase: 07-solver-verification-gate*
*Completed: 2026-03-30*
