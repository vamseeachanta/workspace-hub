# Catenary Solver Canonicalization Investigation

**Issue:** [#2681](https://github.com/vamseeachanta/workspace-hub/issues/2681) — Mooring R5 audit
flagged 7 catenary solver implementations.
**Investigator:** Claude (read-only recon, 2026-05-12)
**Status:** Findings only — no code changes, no commits.

## Executive Summary

The R5 audit slightly undercounted: there are effectively **eight** catenary-related implementations
when you include the modern `marine_analysis/catenary/` package. Three of the seven flagged files
are **byte-identical** (same md5 `b65526edfe70...`), so the de-facto distinct-code count is **5**.

The cleanest path forward is to canonicalize on `digitalmodel/marine_ops/marine_analysis/catenary/`
(modern subpackage, already adapter-fronted) and delete the four legacy `catenary_solver_*` shadow
files plus the orphan `catenary_solver.py` content under the older `marine_engineering/...` path.

## Implementations

| # | File (relative to `digitalmodel/`) | API | Algorithm | Constraint solved | Standards in docstring |
|---|---|---|---|---|---|
| 1 | `src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver.py` | `class CatenarySolver(tolerance, max_iter).solve(CatenaryInput) -> CatenaryResults` | 3-eq fsolve system over `(H, x1, x2)`, falls back to 1-D `brentq` | length + 2D BVP | none (mentions "Excel Poly Mooring" only indirectly via comments) |
| 2 | `.../mooring_analysis/catenary_solver_backup.py` | same names; `tolerance=1e-6, max_iter=100` | scipy `newton` w/ analytical derivative, Brent fallback | **length-only** (ignores Y) | none — references "Excel Poly Mooring (695 array formulas)" |
| 3 | `.../mooring_analysis/catenary_solver_v2.py` | same names; `max_iter=200`; sets `self.gravity` | `brentq` (bracketed) + Newton fallback | **length-only** | none |
| 4 | `.../mooring_analysis/catenary_solver_fixed.py` | same names; safe `sinh`/`cosh` w/ overflow guards | `newton` (analytical `dy/dH`) + Brent fallback; verifies length post-hoc | **vertical-span**, then audits length | none |
| 5 | `.../mooring_analysis/catenary_solver_final.py` | **byte-identical to (1)** | same as (1) | same | same |
| 6 | `src/digitalmodel/marine_ops/marine_analysis/catenary/solver.py` | same names | **byte-identical to (1) & (5)** | same | same |
| 7 | `src/digitalmodel/subsea/mooring_analysis/catenary.py` | `class CatenaryAnalyzer(water_depth).solve_catenary(line, H, z)` + `solve_for_horizontal_tension` + `calculate_stiffness` + `check_touchdown` | analytical `a = H/w`, kN units, hand-rolled Newton in `solve_for_horizontal_tension` | given-H direct + iterative for target tension | **DNV-OS-E301** (ABOUTME line) |
| 8 | `src/digitalmodel/orcaflex/mooring_design.py` (`solve_catenary`) | `def solve_catenary(water_depth, line_length, w, fairlead_depth, pretension) -> CatenaryResult(pydantic)` | inline analytical catenary + hand-rolled 100-iter Newton when pretension supplied | length + (optional) pretension match | **API RP 2SK**, **DNV-OS-E301**, **Faltinsen (1990) Ch. 6** (cited in module + function docstrings) |

> Item (1), (5), and (6) share md5 `b65526edfe70aca47964cfcabdc88ce5`. They are the same file
> committed three times in three different directories. Net distinct implementations: **5**.

## Comparison Matrix

| File | Algorithm | Tests exercising it | Active src/ callers (non-self) | Last meaningful commit | Recommendation |
|---|---|---|---|---|---|
| `mooring_analysis/catenary_solver.py` (1) | fsolve 3-eq + brentq fallback | 0 direct; `mooring_analysis/__init__.py` re-exports it (zero downstream importers in src/ or tests/) | `marine_engineering/__init__.py` re-export only | `41be209b` docstring uplift (#1645), 6w ago; content from `2c185d2d` (7w ago) | **delete after migrating `mooring_analysis/__init__.py`** |
| `catenary_solver_backup.py` (2) | scipy newton (length-only — physically wrong for 2D BVP) | 0 | 0 | `2c185d2d` (7w ago), no later touches | **delete (shadow)** |
| `catenary_solver_v2.py` (3) | brentq+newton (length-only) | 0 | 0 | `41be209b` docstring uplift, `2c185d2d` content | **delete (shadow)** |
| `catenary_solver_fixed.py` (4) | newton on vertical constraint + post-hoc length check | 0 | 0 | `2c185d2d` (7w ago) | **delete (shadow)** |
| `catenary_solver_final.py` (5) | identical to (1) | 0 | 0 | identical history to (1) | **delete (shadow duplicate of (1))** |
| `marine_analysis/catenary/solver.py` (6) | identical to (1) | **5 in `tests/test_catenary_module.py` + 3 in `tests/test_integration_phase1.py` = 8** via `marine_ops.marine_analysis.catenary` package | `marine_analysis/profiling/profile_modules.py`, `marine_analysis/validation/validate_catenary.py` (3 usages), `marine_analysis/visualization/integration_charts.py`, `marine_analysis/catenary/adapter.py`, `subsea/catenary_riser/legacy/catenaryMethods.py` | `2c185d2d` (7w ago) | **CANONICAL — keep** |
| `subsea/mooring_analysis/catenary.py` (7) — `CatenaryAnalyzer` | analytical, kN units, Newton for target tension | 7 in `TestCatenaryAnalyzer` (`tests/subsea/mooring_analysis/test_mooring_analysis_unit.py`) | `subsea/mooring_analysis/cli.py` | `2c185d2d` (7w ago) | **keep — different API surface** (DNV-cited, line-properties-driven; not the same problem as (1)-(6)) |
| `orcaflex/mooring_design.py::solve_catenary` (8) | analytical + Newton when pretension given | 4 in `tests/orcaflex/test_mooring_design.py` (`test_basic_catenary_solution`, `test_catenary_grounded_length`, `test_catenary_short_line_raises`, `test_catenary_with_pretension`) + 1 via `MooringLineDesign.estimate_catenary` (`test_estimate_catenary`) | `MooringLineDesign.estimate_catenary` (same module); `orcaflex/__init__.py` re-export | `bb8e72ad` (6w ago) | **keep — different problem (pretension/anchor-radius design helper, pydantic results)** |

## Canonical Candidate Ranking

Scoring rubric (each 0–3, weighted by audit criteria):

| Implementation | Test coverage | Active callers | Std refs | API cleanliness | Total |
|---|---|---|---|---|---|
| (6) `marine_analysis/catenary/solver.py` | 3 (8 test fns) | 3 (5 src callers) | 0 | 3 (dataclass, scipy.fsolve) | **9** |
| (8) `orcaflex/mooring_design.py::solve_catenary` | 2 (5 test fns) | 2 (1 src caller + re-export) | 3 (API RP 2SK, DNV-E301, Faltinsen) | 2 (pydantic, but uses kN units) | **9** |
| (7) `subsea/mooring_analysis/catenary.py` `CatenaryAnalyzer` | 2 (7 test fns) | 1 (`cli.py`) | 2 (DNV-OS-E301 only) | 2 (richer surface incl. stiffness) | **7** |
| (1) `mooring_analysis/catenary_solver.py` | 0 | 1 (re-export only) | 0 | 3 | **4** |
| (2)/(3)/(4) shadow `_backup`/`_v2`/`_fixed` | 0 | 0 | 0 | 1 each | **1** |
| (5) `catenary_solver_final.py` | 0 (duplicate of (1)) | 0 | 0 | 3 | **3** |

**Top canonical candidate: (6) `digitalmodel/marine_ops/marine_analysis/catenary/solver.py` (score 9).**

Rationale: it (a) already concentrates the test signal (8 test functions), (b) is what the
`adapter.py` deprecation path explicitly points users to, (c) lives under the modern `marine_analysis`
namespace rather than the older `marine_engineering` namespace, and (d) is the algorithm the audit
should treat as the load-bearing 2D BVP solver. (8) ties on score but solves a **different**
problem (anchor-radius design helper with pretension support, pydantic results, kN units, returns
`CatenaryResult` with `top_angle`/`anchor_radius` fields that (6) does not expose). They are
complementary, not redundant.

## Shadow Copies (Delete Candidates)

| # | File | Risk | Notes |
|---|---|---|---|
| (2) | `catenary_solver_backup.py` | none — 0 importers anywhere | length-only solver, physically incorrect for 2D BVP. Pure backup. |
| (3) | `catenary_solver_v2.py` | none — 0 importers | exploration variant, never wired up |
| (4) | `catenary_solver_fixed.py` | none — 0 importers | vertical-only variant, never wired up |
| (5) | `catenary_solver_final.py` | none — 0 importers; identical bytes to (1) | pure shadow of (1) |
| (1) | `catenary_solver.py` (under `mooring_engineering/mooring_analysis/`) | **low** — only consumer is its own `__init__.py` re-export; that re-export has no downstream importers in src/ or tests/ | identical bytes to (6); after fixing the `__init__.py` re-export, this can be deleted too |

**Net: 5 shadow files recommended for deletion** (the four legacy variants plus the duplicate
under the older `marine_engineering` path).

## Active Callers Needing Migration

| Caller | Currently imports | Migration target |
|---|---|---|
| `src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/__init__.py` | `from .catenary_solver import CatenarySolver, CatenaryInput, CatenaryResults` | `from digitalmodel.marine_ops.marine_analysis.catenary import CatenarySolver, CatenaryInput, CatenaryResults` (or drop the re-export and tell consumers to import the modern path directly) |
| `src/digitalmodel/marine_ops/marine_engineering/__init__.py` (re-exports `CatenarySolver`) | indirectly via the above | same — point at `marine_analysis.catenary` |

Tests do not need migration: `tests/test_catenary_module.py` and `tests/test_integration_phase1.py`
already import from `digitalmodel.marine_ops.marine_analysis.catenary` / `marine_engineering.mooring.catenary`
(the modern packages). The only stale reference is in `tests/test_catenary_debug.py`, which is
guarded by a `pytest.importorskip` so it silently skips on the old path — it should be retargeted
or removed.

**Net: 2 active-caller migrations** (both inside `marine_engineering/`'s `__init__.py` files,
both trivial path edits) + 1 stub test cleanup.

## Recommended Deprecation Plan

1. **Pre-flight**: confirm no external repo in workspace-hub imports the
   `marine_engineering.mooring_analysis.catenary_solver` path (verified empty in this investigation).
2. **Migrate the re-exports** in `marine_engineering/__init__.py` and
   `marine_engineering/mooring_analysis/__init__.py` to point at
   `digitalmodel.marine_ops.marine_analysis.catenary`.
3. **Delete the 5 shadow files** in one commit:
   - `catenary_solver.py` (older-namespace duplicate of canonical)
   - `catenary_solver_backup.py`
   - `catenary_solver_v2.py`
   - `catenary_solver_fixed.py`
   - `catenary_solver_final.py`
4. **Retarget or remove** `tests/test_catenary_debug.py` (currently `importorskip`-guarded).
5. **Leave alone** `subsea/mooring_analysis/catenary.py` (`CatenaryAnalyzer`) and
   `orcaflex/mooring_design.py::solve_catenary` — they solve distinct problems and carry their
   own standards citations + test coverage.
6. **Calc citation follow-up**: per `.claude/rules/calc-citation-contract.md`, the canonical solver
   (6) lacks any explicit standards reference in its docstring; once consolidated, a wiki
   citation (DNV-OS-E301 / API RP 2SK) should be wired in.

## Findings (Surprises)

1. **Three of the seven "implementations" are byte-identical** (md5 `b65526edfe70...`):
   `catenary_solver.py`, `catenary_solver_final.py`, and `marine_analysis/catenary/solver.py`.
   The audit treated them as separate copies.
2. **The audit missed an 8th implementation**: `marine_analysis/catenary/solver.py` is the
   modern, test-covered home for the same code — the one the deprecation adapter
   (`marine_analysis/catenary/adapter.py`) already points new users at.
3. **The four "variants" in `mooring_analysis/` are physically different solvers**:
   `_backup` and `_v2` solve a 1-D length-only problem (don't enforce the vertical span),
   `_fixed` solves the vertical-span constraint and then audits length, and the base
   `catenary_solver.py` / `_final` solve the full 3-equation 2D BVP. They produce **different
   tension answers** for the same inputs and are not interchangeable copies.
4. The `marine_engineering.mooring_analysis` re-export module (which the audit treated as the
   "live" path) has **zero downstream importers** in either `src/` or `tests/` — it's dead
   surface area pointing at a duplicate of (6).
5. `CatenaryAnalyzer` (subsea) uses **kN** internally while `CatenarySolver` (marine_analysis)
   uses **N** — a unit-discipline footgun if the two ever get aliased.

## File Inventory (for the cleanup PR)

Files referenced (absolute paths):

- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_analysis/catenary/solver.py` — **CANONICAL**
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_analysis/catenary/__init__.py`
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_analysis/catenary/adapter.py`
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/__init__.py` — needs import-path edit
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/__init__.py` — needs import-path edit
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver.py` — delete
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver_backup.py` — delete
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver_v2.py` — delete
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver_fixed.py` — delete
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/marine_ops/marine_engineering/mooring_analysis/catenary_solver_final.py` — delete
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/subsea/mooring_analysis/catenary.py` — **keep** (`CatenaryAnalyzer`, distinct API)
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/orcaflex/mooring_design.py` — **keep** (`solve_catenary`, distinct API)
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/test_catenary_debug.py` — retarget or remove (importorskip-guarded against the dead path)
