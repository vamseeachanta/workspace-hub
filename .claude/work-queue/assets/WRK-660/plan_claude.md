# WRK-660 Plan: Test Coverage Gap Audit — 5 Untested assetutilities Modules

## Route B — Inline Plan (v2, post cross-review)

### Scope
Target: 4 modules with confirmed 0% coverage (units excluded — already 82-100% covered).
- calculations: most files 0%, scr_fatigue 39%
- devtools: 5 files all 0%
- base_configs: nested modules all 0%
- tools: git/, pdf/ subdirs 0%

### Phase 0 — Coverage Baseline
Run pytest --cov, record per-module % before any changes.
Baseline saved: specs/wrk/WRK-660/coverage-baseline.txt

### Phase 1 — Gemini Test Plan Generation
Pipe coverage gaps + source files + reference tests into Gemini.
Gemini generates complete test functions (with assertions) targeting uncovered lines.
Output: specs/wrk/WRK-660/test-coverage-gap-plan.md

### Phase 2 — Overlap Validation
grep -hoP '(?<=def )test_\w+' to extract function names only.
sort both lists, comm -13 to find collisions. Empty output = safe.

### Phase 3 — Scaffold and Verify
Create 4 test files under tests/modules/{module}/test_{module}_coverage.py
Run full pytest (not --collect-only) — must exit 0 with real assertions.
Re-run --cov, confirm coverage delta > 0 for each module.

### Cross-Review Findings (Addressed)
- Claude P2: ACs strengthened (full run, not collect-only; coverage delta required)
- Gemini MINOR: function name extraction improved; test paths clarified
