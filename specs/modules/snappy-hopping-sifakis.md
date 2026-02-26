# Plan: File-Structure Skill Hardening + Repo Structural Remediation

**WRK scope**: New WRK items to be captured (no duplicates — WRK-368 done, file-taxonomy v1.1.0 exists)
**Repos in scope**: `digitalmodel`, `worldenergydata`
**Skills in scope**: `file-taxonomy` (v1.1.0), `repo-structure` (v1.0.0, from WRK-368)
**Evidence basis**: Direct folder tree exploration + git log (last 30–50 commits) + skill content audit

---

## Context

Both repos have active development but no *enforced* canonical paths. The `file-taxonomy`
and `repo-structure` skills exist as documentation but have no validation layer — files
continue to land in wrong or inconsistent locations. Git history shows this is a moving
problem: new modules added in Feb 2026 (dashboard, economics, eia, well/) each introduced
fresh inconsistencies even while older ones remain unresolved.

**User-confirmed problem categories**: configs, input files, analysis scripts, benchmarking,
specs, output files, results, docs. Each category has a different failure mode per repo.

---

## Evidence: Confirmed Structural Issues (git-verified)

### digitalmodel

| # | Issue | Location | How Detected |
|---|-------|----------|-------------|
| D1 | Dual test root — `tests/unit/well/` (WRK-377) AND `tests/well/` both active | `tests/` | git log `f23bc43` |
| D2 | Tests inside `src/` — `asset_integrity/tests/` in src tree | `src/digitalmodel/asset_integrity/tests/` | Direct exploration |
| D3 | `docs/modules/` stale residue after `docs/domains/` rename | `docs/modules/orcawave/`, `docs/modules/references/` | git log `e2edf6a` |
| D4 | `docs/sub_*` prefix dirs — legacy pre-domains pattern | `docs/sub_coiled_tubing/`, `docs/sub_drilling/`, etc. | Direct exploration |
| D5 | `tests/subsea/mooring/` AND `tests/subsea/mooring_analysis/` — only one exists in `src/` | `tests/subsea/` | Direct exploration |
| D6 | `visualization/orcaflex-dashboard/` — kebab-case in snake_case package tree | `src/digitalmodel/visualization/` | Direct exploration |
| D7 | `infrastructure/` monolith — 40+ subdirs mixing config, solvers, services, validation | `src/digitalmodel/infrastructure/` | Direct exploration |
| D8 | `specs/modules/` nearly empty — no architecture specs | `specs/` | Direct exploration |
| D9 | `tests/output/` and `tests/outputs/` — generated artifacts committed to tests/ | `tests/output/`, `tests/outputs/` | git history |
| D10 | `tests/phase2/`, `tests/phase3/` — unnamed catch-all dirs | `tests/` | Direct exploration |

### worldenergydata

| # | Issue | Location | How Detected |
|---|-------|----------|-------------|
| W1 | **Three-tier test inconsistency** — `tests/unit/<mod>/` (canonical) vs `tests/modules/<mod>/` (older) vs `tests/<mod>/` (newest deviations: dashboard, economics, eia) | `tests/` | git log (Feb 2026 commits) |
| W2 | `tests/agent_os/` orphaned — src deleted in WRK-344, tests not cleaned | `tests/agent_os/` | git log `a5446a5` |
| W3 | Triple fixture locations — `test_data/` (root-level) + `tests/data/` + `tests/fixtures/` | `tests/`, root | Direct exploration |
| W4 | `results/` at repo root contains committed artifacts (`results/Data/`, `results/Plot/`) | `results/` | Direct exploration |
| W5 | Dual validation packages — `src/worldenergydata/validation/` (old) + `src/worldenergydata/common/validation/` (post-WRK-345) | `src/worldenergydata/` | git log `24bef28` |
| W6 | Duplicate archive dirs — `tests/_archived/`, `tests/_archived_tests/`, `tests/legacy_tests/` | `tests/` | Direct exploration |
| W7 | `src/worldenergydata/modules/` — catch-all package at same level as domain packages | `src/worldenergydata/` | Direct exploration |
| W8 | `eia/` vs `eia_us/` — two parallel EIA packages, no clear split | `src/worldenergydata/eia/`, `eia_us/` | git log `c149b32` |
| W9 | WRK deliverable in `docs/` — `docs/wrk-083-export-validation-report.md` | `docs/` | Direct exploration |
| W10 | `specs/modules/` empty — no module specs despite 906 src modules | `specs/` | Direct exploration |
| W11 | `test_output/` at repo root (separate from `results/`) | root | Direct exploration |
| W12 | Config files scattered: `config/ai_agents/`, `config/analysis/`, `config/input/`, `config/scheduler/`, `config/validation/` — good structure BUT `well_production_dashboard/config/` also exists inside `src/` | `config/`, `src/` | Direct exploration |

---

## Proposed WRK Items (no duplicates with existing queue)

### Group A — Quick Wins (Route A, batch-able, no import breakage)

**WRK-NEW-A1: Clean orphaned tests/agent_os/ in worldenergydata**
- `rm -rf tests/agent_os/` (src was archived in WRK-344; tests/ not cleaned)
- Add test to confirm no import references remain
- Computer: ace-linux-1

**WRK-NEW-A2: Consolidate worldenergydata test archive dirs**
- Merge `tests/_archived/` + `tests/_archived_tests/` + `tests/legacy_tests/` → single `tests/_archive/`
- Complexity: Simple

**WRK-NEW-A3: Delete worldenergydata committed result artifacts**
- Move `results/Data/`, `results/Plot/` out of git tracking; add `results/` to `.gitignore`
- Add `test_output/` to `.gitignore`
- Complexity: Simple

**WRK-NEW-A4: Move WRK deliverable out of worldenergydata docs/**
- `docs/wrk-083-export-validation-report.md` → `.claude/work-queue/done/`
- Complexity: Simple

**WRK-NEW-A5: Remove docs/modules/ stale residue in digitalmodel**
- Delete `docs/modules/orcawave/`, `docs/modules/references/` (left after `docs/domains/` rename)
- Complexity: Simple

**WRK-NEW-A6: Rename docs/sub_* prefix dirs in digitalmodel**
- Rename `docs/sub_coiled_tubing/` → `docs/domains/coiled_tubing/`, etc. (align with post-rename pattern)
- Complexity: Simple

**WRK-NEW-A7: Fix kebab-case dir in digitalmodel src/**
- Rename `visualization/orcaflex-dashboard/` → `visualization/orcaflex_dashboard/`
- Complexity: Simple

### Group B — Medium Refactors (Route B, some import fixes needed)

**WRK-NEW-B1: Resolve worldenergydata three-tier test inconsistency**
- Canonical: `tests/unit/<module>/`
- Move `tests/modules/<module>/` → `tests/unit/<module>/` (many modules)
- Move `tests/dashboard/`, `tests/economics/`, `tests/eia/` → `tests/unit/`
- Fix imports after move; run full test suite
- Computer: ace-linux-1

**WRK-NEW-B2: Resolve worldenergydata dual validation packages**
- `src/worldenergydata/validation/` is the old package (pre-WRK-345)
- `src/worldenergydata/common/validation/` is canonical (post-WRK-345)
- Migrate any remaining callers from `validation/` → `common/validation/`, then delete `validation/`
- Computer: ace-linux-1

**WRK-NEW-B3: Consolidate worldenergydata fixture/data dirs**
- Canonical: `tests/fixtures/<domain>/` for static test data
- Move `test_data/` (root-level) → `tests/fixtures/`; remove `tests/data/` duplicates
- Update imports/fixture paths in affected tests
- Computer: ace-linux-1

**WRK-NEW-B4: Resolve digitalmodel dual test root (tests/ vs tests/unit/)**
- `tests/unit/well/` (WRK-377 pattern) conflicts with `tests/well/` (all other modules)
- Decision: adopt `tests/<domain>/` as canonical (matches 95% of existing modules)
- Move `tests/unit/well/` → `tests/well/`; remove `tests/unit/` dir
- Computer: ace-linux-1

**WRK-NEW-B5: Remove tests inside digitalmodel src/**
- Move `src/digitalmodel/asset_integrity/tests/` → `tests/asset_integrity/`
- Enforce in repo-structure skill: no `tests/` inside `src/`
- Computer: ace-linux-1

**WRK-NEW-B6: Clean digitalmodel tests/subsea/ ghost dirs**
- `tests/subsea/mooring/` has no src counterpart (only `mooring_analysis/` exists)
- Merge or delete; align with `src/digitalmodel/subsea/mooring_analysis/`
- Computer: ace-linux-1

**WRK-NEW-B7: Clean digitalmodel tests/phase2/, tests/phase3/, tests/output/**
- `tests/phase2/`, `tests/phase3/` — unnamed catch-all; contents → appropriate domain dirs
- `tests/output/`, `tests/outputs/` — generated artifacts; add to `.gitignore`
- Computer: ace-linux-1

**WRK-NEW-B8: Clarify worldenergydata eia/ vs eia_us/ split**
- `eia/` (Feb 2026) vs `eia_us/` (older) — document clear split or merge
- Define: `eia_us/` = US-only BSEE/RRC/EIA data; `eia/` = international EIA API client
- If roles overlap → merge; if distinct → add `__init__.py` docstrings clarifying scope
- Computer: ace-linux-1

**WRK-NEW-B9: Remove worldenergydata src modules/ catch-all**
- `src/worldenergydata/modules/` — undefined responsibility alongside domain packages
- Audit contents; migrate to appropriate domain packages; delete
- Computer: ace-linux-1

### Group C — Skill Hardening (Route A/B, main session)

**WRK-NEW-C1: Add config/ canonical path to file-taxonomy skill**
- Current gap: config files not covered (files land in root, `config/`, `tests/`, inline)
- Canonical: `config/<domain>/` for runtime YAML/JSON, root-only for `pyproject.toml`/`pytest.ini`
- Exception: `src/<pkg>/<module>/config/` ONLY if config is package-internal and not user-facing
- Version bump: file-taxonomy v1.1.0 → v1.2.0

**WRK-NEW-C2: Add analysis/ and benchmarks/ canonical paths to file-taxonomy skill**
- Analysis scripts: `scripts/analysis/<domain>/` (exploratory); `notebooks/<domain>/` (Jupyter)
- Benchmarks: `tests/benchmarks/<domain>/` (single home, both repos)
- Input files: `data/inputs/<domain>/` for runtime; `tests/fixtures/<domain>/` for test data
- Version bump: file-taxonomy v1.2.0 → v1.3.0

**WRK-NEW-C3: Add enforcement section to repo-structure skill**
- Add "Enforcement" section documenting: no `tests/` in `src/`, no generated files in `tests/`,
  single test root (`tests/<domain>/` not `tests/unit/`), no catch-all dirs (`modules/`, `phase2/`)
- Version bump: repo-structure v1.0.0 → v1.1.0

**WRK-NEW-C4: File placement validation script**
- `scripts/operations/validate-file-placement.sh`
- Checks per repo: generated artifacts in tests/output (fail), tests inside src/ (fail),
  WRK files in docs/ (warn), results/ not gitignored (warn), kebab-case in src (warn)
- Integrates with pre-commit hook
- Computer: ace-linux-1

### Group D — Long Horizon (Route C, architectural)

**WRK-NEW-D1: Break up digitalmodel infrastructure/ monolith**
- Split 40+ subdirs into domain-aligned modules
- High import chain complexity; requires full test suite as safety net
- Computer: ace-linux-1 (long session)

**WRK-NEW-D2: Populate specs/modules/ in both repos**
- Digitalmodel: architecture specs for top-5 domains (infrastructure, hydrodynamics, structural, subsea, well)
- Worldenergydata: data-source specs per jurisdiction (bsee, eia_us, metocean, sodir, vessel_fleet)
- Computer: ace-linux-1

---

## Execution Order

```
Phase 1 (immediate): A1–A7 — deletions, renames, no code breakage
Phase 2 (next sprint): C1–C4 — skill updates + validation script
Phase 3 (following):  B1–B5 — test restructuring (import fixes needed)
Phase 4 (following):  B6–B9 — remaining medium refactors
Phase 5 (long):       D1–D2 — architectural changes
```

---

## What the Skills Need (Gap vs Current v1.1.0/v1.0.0)

| Gap | Skill to Update | Section to Add |
|-----|----------------|----------------|
| No canonical path for config files | file-taxonomy | `config/` → `config/<domain>/` |
| No canonical path for analysis scripts | file-taxonomy | `scripts/analysis/<domain>/` |
| No canonical path for notebooks | file-taxonomy | `notebooks/<domain>/` |
| No canonical path for input files | file-taxonomy | `data/inputs/<domain>/` |
| No rule against tests inside src/ | repo-structure | Enforcement section |
| No rule against generated files in tests/ | repo-structure | Enforcement section |
| No rule against catch-all dirs in src/ | repo-structure | Enforcement section |
| No validation tooling | new script | `scripts/operations/validate-file-placement.sh` |

---

## Critical Files Referenced

| File | Purpose |
|------|---------|
| `.claude/skills/workspace-hub/file-taxonomy/SKILL.md` | Canonical output placement (update to v1.2.0→v1.3.0) |
| `.claude/skills/workspace-hub/repo-structure/SKILL.md` | Source layout rules (update to v1.1.0) |
| `digitalmodel/tests/unit/well/` | Move to `tests/well/` (WRK-NEW-B4) |
| `digitalmodel/src/digitalmodel/asset_integrity/tests/` | Move to `tests/asset_integrity/` (WRK-NEW-B5) |
| `worldenergydata/tests/agent_os/` | Delete (WRK-NEW-A1) |
| `worldenergydata/tests/modules/` | Move to `tests/unit/` (WRK-NEW-B1) |
| `worldenergydata/src/worldenergydata/validation/` | Merge into `common/validation/` (WRK-NEW-B2) |
| `worldenergydata/results/` | Gitignore + remove committed artifacts (WRK-NEW-A3) |
