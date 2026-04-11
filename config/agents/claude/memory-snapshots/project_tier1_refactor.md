---
name: Tier-1 repos deep refactor
description: Cross-repo modernization of digitalmodel, assetutilities, worldenergydata — Phase 1 complete, Phase 2 ready to execute
type: project
originSessionId: 2aada347-9175-42ad-9ee3-68fa8157944e
---
Phase 1 (assetutilities) complete as of 2026-04-09. Phase 2A (digitalmodel) and Phase 2B (worldenergydata) ready to execute in parallel.

**Why:** Modernize all 3 tier-1 repos with consistent quality — packaging, types, tests, docs, CI, clean architecture.

**How to apply:** Use next session prompt below to continue. Always check assetutilities/main for latest state before starting Phase 2.

## Phase Status

| Phase | Repo | Status | Commits |
|-------|------|--------|---------|
| 1 | assetutilities | COMPLETE (2026-04-09) | 9 commits on main |
| 2A | digitalmodel | NOT STARTED | — |
| 2B | worldenergydata | NOT STARTED | — |

## Phase 1 Results (assetutilities)

Commits on assetutilities/main:
- `d15de99` fix(packaging): remove pytest from core deps and delete stale setup.py
- `7c3c2e5` fix(packaging): pin all dependencies with upper bounds, fix black target
- `06d17de` refactor(common): decompose data.py into focused typed modules (16 classes → 8 modules)
- `c3efe10` refactor(agent_os): decompose context_optimization into 4 focused modules
- `94442dd` refactor(agent_os): decompose specs_integration into 5 focused modules
- `af06200` refactor(agent_os): decompose template_management into 6 focused modules
- `6e312da` refactor(agent_os): decompose documentation_integration into 5 focused modules
- `17a2e8f` refactor(agent_os): decompose cli.py into 7 focused modules
- `bfa85d8` chore: remove stale root-level documentation files

Tests: 1211 passed, 3 skipped, 0 failed.

## Key Artifacts

- Design spec: `workspace-hub/docs/superpowers/specs/2026-04-09-tier1-deep-refactor-design.md`
- Plan 2A: `workspace-hub/docs/superpowers/plans/2026-04-09-plan2a-digitalmodel-refactor.md`
- Plan 2B: `workspace-hub/docs/superpowers/plans/2026-04-09-plan2b-worldenergydata-refactor.md`

## Next Session Prompt

```
Resume tier-1 deep refactor — Phase 1 (assetutilities) is complete (9 commits on 
assetutilities/main, 1211 tests passing).

Execute Phase 2A and Phase 2B in parallel as isolated worktree agents:

Phase 2A (digitalmodel) — plan at:
  docs/superpowers/plans/2026-04-09-plan2a-digitalmodel-refactor.md
  Tasks: deduplicate 17 conflicting deps, align version targets (3.11+),
  type orcaflex.py + aqwa_router.py, clean --version.* artifacts,
  triage collect_ignore list, final verification.

Phase 2B (worldenergydata) — plan at:
  docs/superpowers/plans/2026-04-09-plan2b-worldenergydata-refactor.md
  Tasks: create data_resolver.py (WED_DATA_ROOT > symlink > fallback),
  migrate 40+ hardcoded paths, consolidate bsee/ + marine_safety/ modules,
  replace 487 print() with loguru logging, fix packaging (local assetutilities dep,
  pin all, mypy blocks CI), add validation layer tests (0% → covered).

Dispatch both as parallel gsd-executor agents with isolation=worktree.
```
