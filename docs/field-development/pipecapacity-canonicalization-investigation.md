# PipeCapacity Canonicalization Investigation

**Issue:** [#2692](https://github.com/vamseeachanta/workspace-hub/issues/2692) — Subsea Pipelines R5 audit
flagged 5 PipeCapacity implementations under [#2694](https://github.com/vamseeachanta/workspace-hub/issues/2694).
**Investigator:** Claude (read-only recon, 2026-05-13)
**Status:** Findings only — no code changes, no commits.

## Executive Summary

`digitalmodel` contains **5 files named `PipeCapacity.py` / `pipe_capacity.py`** across two packages
(`structural/pipe_capacity/` and `asset_integrity/`). All 5 have distinct md5s — no byte-identical
duplicates — but only **one is on the live engine routing path** (`custom/PipeCapacity.py` under
`structural/pipe_capacity/`). The other four split as:

- 1 thin orchestrator (`pipe_capacity.py`) — **live entry point**, 17 LOC, called by `engine.py`
- 1 reachable solver (`structural/.../custom/PipeCapacity.py`) — **load-bearing**, includes the
  unique `DNVWallThickness` (DNV-OS-F101/F201) class with 2 dedicated test files
- 3 unreachable solvers (top-level `PipeCapacity.py`, `common/PipeCapacity.py`,
  `asset_integrity/custom/PipeCapacity.py`) — **shadows with zero non-self callers in `src/`**

The most insidious detail: `common/PipeCapacity.py` (1,192 LOC) has a **broken import** at line 7
(`from common.update_deep import update_deep_dictionary` — no such top-level `common` module
in the importable namespace). Its dedicated test file (`test_pipe_capacity_common.py`,
1,773 LOC, 103 tests) compensates by sys.path-hacking `src/digitalmodel/infrastructure/` onto
the path. Any normal consumer importing this module would crash on import. This is dead-on-arrival
code with extensive test coverage running against a path that no production caller traverses.

The cleanest path forward is to canonicalize on `structural/pipe_capacity/custom/PipeCapacity.py`
(the only file actually invoked by `engine.py` via the orchestrator) and treat the other three
solver variants as shadows.

## Implementations

| # | File (relative to `digitalmodel/src/digitalmodel/`) | LOC | md5 | Role |
|---|---|---|---|---|
| 1 | `structural/pipe_capacity/PipeCapacity.py` | 679 | `605416c1...` | Top-level shadow solver. No active callers. Imports `digitalmodel.infrastructure.utils.update_deep` (path **works**), but no production code routes to it. |
| 2 | `structural/pipe_capacity/pipe_capacity.py` | 17 | `1a77998b...` | **Live entry point.** Thin orchestrator: `class PipeCapacity: router(cfg) → pipe_comps.evaluate_pipe_capacity(cfg)`. Imported by `engine.py` (line 28) and `__init__.py` (line 51). |
| 3 | `structural/pipe_capacity/common/PipeCapacity.py` | 1,192 | `5e0ea3c4...` | Solver duplicate of (1) with PEP-8 reformatting. **Broken import** `from common.update_deep import update_deep_dictionary` — no top-level `common` package. Only its dedicated test (`test_pipe_capacity_common.py`) imports it via sys.path hack. |
| 4 | `structural/pipe_capacity/custom/PipeCapacity.py` | 1,479 | `cf9bbfe8...` | **Load-bearing solver.** Reached via `pipe_components.py` → `evaluate_pipe_capacity()`. Adds unique `DNVWallThickness` class (DNV-OS-F101/F201) — only this file has it. Has 2 test files (`test_pipe_capacity_custom.py` 108 tests + `test_pipe_capacity_dnv.py` 5 tests + `test_pipe_capacity_codes.py` 7 tests = 120 tests). |
| 5 | `asset_integrity/custom/PipeCapacity.py` | 863 | `e7c6a1bd...` | Older fork of (4) **without** `DNVWallThickness`. Imported only by `asset_integrity/common/pipe_components.py` (which has 0 callers in `src/`). Has indirect tests via `tests/asset_integrity/test_calculations.py` (29 tests). |

**Byte-identical groups:** none. All 5 files have unique md5s.

**Algorithmic distinctness:** 4 of 5 contain a `PipeCapacity` class with the same public surface
(`evaluate_pipe_wall`, `internal_pressure`, `external_pressure`, `collapse_propagation`) plus
auxiliary code-specific classes (`API_RP_16Q`, `API_TR_5C3`, `VonMises_Pipe`, `CFR_30_Part_250`,
`InternalPressureMethods`, `OtherMethodsTobeIncorporated`, `API_RP_2RD`). File (2) is a thin
17-line orchestrator with a different role (router, not solver).

## Comparison Matrix

| File | Public classes / surface | Standards refs in docstrings/code | Test coverage | Active `src/` callers (non-self) | Last meaningful commit | Recommendation |
|---|---|---|---|---|---|---|
| (1) `structural/.../PipeCapacity.py` | `PipeCapacity` + 7 aux classes | API RP 1111-2009, API STD 2RD-2013, API RP 16Q-2017, API TR 5C3-2018, ASME B31, 30 CFR Part 250 (all as string-match dispatch, no docstring narration) | **0** (no test file imports this path) | 0 (only self-imports `PipeSizing` at line 556) | `37136c85` docstring uplift (6 weeks ago) | **DELETE (shadow)** — content superset of (5), missing DNV class of (4) |
| (2) `structural/.../pipe_capacity.py` | `PipeCapacity.router(cfg) → cfg` (orchestrator) | none | 0 direct (exercised indirectly via engine integration tests) | **2** (`engine.py:28`, `__init__.py:51`) | `37136c85` docstring uplift (6 weeks ago) | **KEEP — distinct role** (entry point, not solver) |
| (3) `structural/.../common/PipeCapacity.py` | `PipeCapacity` + 7 aux classes | same set as (1) (ASME B31, API 1111/2RD/16Q/5C3, 30 CFR Part 250) | 103 tests in `test_pipe_capacity_common.py` (1,773 LOC) — but **only via sys.path hack** | 0 (broken-import path) | `37136c85` docstring uplift; `06aa07df` Pint refactor (6 weeks ago) | **DELETE (shadow)** — broken import, no production reach. Tests should be migrated to (4) or retargeted. |
| (4) `structural/.../custom/PipeCapacity.py` | `PipeCapacity` + `DNVWallThickness` + 7 aux classes + 4 module-level helpers (`_is_dnv_f101`, `_is_dnv_f201`, `_extract_year_from_code`, `_resolve_pressure_value`) | ASME B31, API 1111/2RD/16Q/5C3, 30 CFR Part 250, **DNV-OS-F101**, **DNV-ST-F101**, **DNVGL-ST-F101**, **DNV-OS-F201** (string-match dispatch); design-factor defaults documented inline | **120 tests** total: `test_pipe_capacity_custom.py` (108), `test_pipe_capacity_codes.py` (7), `test_pipe_capacity_dnv.py` (5) | `pipe_components.py:6` (which is reached from the live orchestrator) | `37136c85` docstring uplift; `06aa07df` Pint refactor (6 weeks ago) | **CANONICAL — keep** |
| (5) `asset_integrity/custom/PipeCapacity.py` | `PipeCapacity` + 7 aux classes (**no DNV**) | ASME B31, API 1111/2RD/16Q/5C3, 30 CFR Part 250 (no DNV-F101/F201) | 29 tests in `tests/asset_integrity/test_calculations.py` | `asset_integrity/common/pipe_components.py:4` — but **that pipe_components has zero callers in `src/`** | `2c6af5a0` docstring uplift; `06aa07df` Pint refactor (6 weeks ago) | **DELETE (shadow)** — older fork of (4) lacking DNV. Tests reachable only because they import (5) directly, not via any production routing. |

## Canonical Candidate Ranking

Scoring rubric (each 0–3):

| Implementation | Test coverage | Active callers | Std refs | API cleanliness / completeness | Total |
|---|---|---|---|---|---|
| (4) `structural/.../custom/PipeCapacity.py` | 3 (120 tests across 3 files) | 3 (live engine path via orchestrator + pipe_components) | 3 (ASME, API ×4, DNV-F101/F201, 30 CFR — most complete) | 3 (largest, has DNV class) | **12** |
| (2) `structural/.../pipe_capacity.py` | 1 (indirect engine tests) | 3 (engine.py + __init__.py) | 0 | 2 (correct role: orchestrator) | **6** |
| (5) `asset_integrity/custom/PipeCapacity.py` | 2 (29 tests) | 1 (dead-end pipe_components) | 2 (no DNV) | 2 | **7** |
| (1) `structural/.../PipeCapacity.py` | 0 | 0 | 2 | 2 | **4** |
| (3) `structural/.../common/PipeCapacity.py` | 1 (103 tests but via path hack on broken import) | 0 (broken import) | 2 | 2 | **5** |

**Top canonical candidate (solver): (4) `structural/pipe_capacity/custom/PipeCapacity.py` (score 12).**

Rationale: it is (a) the only file actually exercised by the live engine routing
(`engine.py → pipe_capacity.py → pipe_components.py → custom/PipeCapacity.py`), (b) the only one
containing the `DNVWallThickness` implementation (DNV-OS-F101/F201 — a regulatorily-required code
for offshore pipelines), (c) has by far the most test coverage (120 tests across 3 files), and
(d) carries the most complete standards-dispatch surface (adds DNV to the common ASME/API/CFR set).

**Note:** (2) `pipe_capacity.py` solves a **different problem** (orchestrator routing, not pipe
capacity computation). It should be kept and is complementary to (4), not redundant. The 5-way
count is misleading — there is functionally 1 orchestrator + 4 solvers, of which 1 solver is live.

## Shadow Copies (Delete Candidates)

| # | File | Risk | Notes |
|---|---|---|---|
| (1) | `structural/.../PipeCapacity.py` | none — 0 importers anywhere | older naming/case duplicate of (4) without the DNV class. Pure shadow. |
| (3) | `structural/.../common/PipeCapacity.py` | **none for production**; **medium for tests** — 103 tests import via sys.path hack | broken import (`from common.update_deep`) means it cannot be imported normally. Delete after migrating test cases to exercise (4) — the tests are valuable, the module is not. |
| (5) | `asset_integrity/custom/PipeCapacity.py` | **low** — only consumer is `asset_integrity/common/pipe_components.py` which itself has 0 callers in `src/` | older fork of (4) missing DNV. Delete after confirming `asset_integrity/common/pipe_components.py` is dead and the 29 tests in `test_calculations.py` are either migrated or deleted. |

**Net: 3 shadow solver files recommended for deletion** plus dead `asset_integrity/common/pipe_components.py`.

## Active Callers Needing Migration

| Caller | Currently imports | Migration target / action |
|---|---|---|
| `tests/structural/pipe_capacity/test_pipe_capacity_common.py` | `from digitalmodel.structural.pipe_capacity.common.PipeCapacity import (PipeCapacity, API_RP_2RD, API_RP_16Q, API_TR_5C3, CFR_30_Part_250, InternalPressureMethods, OtherMethodsTobeIncorporated)` via sys.path hack | retarget to `digitalmodel.structural.pipe_capacity.custom.PipeCapacity` (same class names exist there); remove the sys.path hack |
| `tests/asset_integrity/test_calculations.py` (7 import sites) | `from digitalmodel.asset_integrity.custom.PipeCapacity import PipeCapacity` | either retarget to `digitalmodel.structural.pipe_capacity.custom.PipeCapacity` (same class) or delete the tests if `asset_integrity` is a deprecated package surface |
| `src/digitalmodel/asset_integrity/common/pipe_components.py` | `from ..custom.PipeCapacity import PipeCapacity` | this module is itself unused — delete it along with (5) |

**Net: 2 test-file migrations** (both trivial path edits — same class API) + 1 dead `pipe_components.py` deletion.

No `src/` non-test callers need migration. The orchestrator (2) and `common/pipe_components.py`
(the live one) already point at (4) via `from digitalmodel.structural.pipe_capacity.custom.PipeCapacity import PipeCapacity`.

## Recommended Deprecation Plan (mirrors #2686)

### Phase 1: Delete obvious shadows (safe — 0 production callers)

1. **`structural/pipe_capacity/PipeCapacity.py`** (top-level case-variant shadow of (4) without DNV).
   Pre-flight: confirm no external repo imports `digitalmodel.structural.pipe_capacity.PipeCapacity`
   (the dotted path; case-sensitive). It also self-imports `PipeSizing` at line 556 — that
   `PipeSizing` is at the same level (`structural/pipe_capacity/PipeSizing.py`), separate from
   `custom/PipeSizing.py`. Verify the case-sensitive name clash doesn't break Python on Linux
   (it doesn't on case-insensitive filesystems but `pipe_capacity.py` and `PipeCapacity.py`
   coexist; deleting the latter clears the ambiguity).

### Phase 2: Migrate then delete the broken-import shadow

2. **Retarget `tests/structural/pipe_capacity/test_pipe_capacity_common.py`** to import from
   `digitalmodel.structural.pipe_capacity.custom.PipeCapacity` (same class names, real import path,
   no sys.path hack needed). The 103 tests are valuable; the module is not.
3. **Delete `structural/pipe_capacity/common/PipeCapacity.py`** once tests run green against (4).

### Phase 3: Migrate then delete the asset_integrity fork

4. **Decide on `asset_integrity/` package surface:** if it's a deprecated alias for
   `structural/pipe_capacity`, retarget the 7 imports in `tests/asset_integrity/test_calculations.py`
   to `digitalmodel.structural.pipe_capacity.custom.PipeCapacity`. If `asset_integrity/` is
   intentionally distinct (per #2692 audit, it appears to be older code), document the rationale.
5. **Delete `src/digitalmodel/asset_integrity/common/pipe_components.py`** (0 src/ callers).
6. **Delete `src/digitalmodel/asset_integrity/custom/PipeCapacity.py`** once tests are migrated.

### Phase 4: DNV edition discipline (parallel to cathodic-protection edition decision in #2694)

7. **Audit `DNVWallThickness._resolve_design_factors`** — defaults are hard-coded
   (`gamma_m=1.15`, `gamma_sc=1.046`, `alpha_u=0.96`, `alpha_fab=1.0`, `alpha_mpt=0.75`,
   `alpha_spt=1.0`, `ovality=0.005`). These are DNV-OS-F101 numerics; need to verify which
   edition (2017, 2021) and emit a `Citation` per `.claude/rules/calc-citation-contract.md`.
   The class uses `_extract_year_from_code()` to read the year from the specification-code string,
   but the defaults don't change by year — silent edition-drift hazard, mirroring the cathodic-
   protection cluster in #2694.

### Phase 5: Calc-citation follow-up

8. Per `.claude/rules/calc-citation-contract.md`, none of the 5 files emit `Citation` instances
   despite using DNV-OS-F101, API RP 1111, API STD 2RD, API RP 16Q, API TR 5C3, 30 CFR Part 250,
   ASME B31.4/.8 constants. Once consolidated on (4), wiki citations should be wired in for at
   least the DNV partial-safety factors and the API RP 1111 strain-based design transition.

## Findings (Surprises)

1. **The 5-way count is misleading.** It's really **1 orchestrator + 4 solver variants**, of which
   only **1 solver is on the live execution path**. The orchestrator (`pipe_capacity.py`, 17 LOC)
   was counted as a sibling to the solvers but is functionally distinct — it's the entry point
   `engine.py` actually invokes.

2. **`common/PipeCapacity.py` is a broken-import zombie.** 1,192 LOC of solver code that cannot
   be imported normally because of `from common.update_deep import update_deep_dictionary` on
   line 7 (no top-level `common` package in the import namespace). Its dedicated test file
   (1,773 LOC, 103 tests) sys.path-hacks `src/digitalmodel/infrastructure/` onto `sys.path` to
   resolve the import. Any normal consumer would crash on import. This means **the 103 tests
   are validating dead-on-arrival code** — they pass, but nothing in production exercises this
   module. Hazard: someone reads the test passes as "this code is validated and working".

3. **Only `custom/` has DNV-OS-F101/F201.** Files (1), (3), and (5) lack the `DNVWallThickness`
   class entirely. If a project config specifies a `DNV-OS-F101-...` spec code and the consumer
   somehow routed to one of the shadows, the dispatch chain would silently fall through with
   `minimum_thickness` and `pressure` unbound — a `NameError` at calc time. This is a latent
   regulatory-coverage hazard, not just code clutter.

4. **`asset_integrity/custom/PipeCapacity.py` (863 LOC) is an older fork of `structural/.../custom/PipeCapacity.py` (1,479 LOC).**
   The diff is ~1,525 substantive lines, almost entirely accounted for by the DNV additions in (4).
   `asset_integrity` predates the DNV uplift. Tests in `test_calculations.py` validate the older
   API surface; if `asset_integrity/` is meant to be the "field integrity" package, it has
   silently fallen behind the structural-design path on standards coverage.

5. **DNV partial-safety factors are hard-coded with no edition discriminator** in `DNVWallThickness._resolve_design_factors`.
   The function calls `_extract_year_from_code()` to extract the year from the spec-code string and
   constructs lookup keys like `DNV-OS-F101-2017`, but the `defaults` dict baked into the function
   uses the same values regardless of year. This is the same defect class as the cathodic-protection
   2017-vs-2021 edition drift flagged in #2694's parent table — silent edition shadow.

6. **The "live" path is shallower than the file count suggests:** `engine.py` → `pipe_capacity.PipeCapacity.router(cfg)`
   → `pipe_comps.evaluate_pipe_capacity(cfg)` (in `common/pipe_components.py`)
   → instantiates `custom.PipeCapacity(cfg).evaluate_pipe_wall()`. Three of the four solver files
   are entirely off this path.

## File Inventory (for the cleanup PR)

Files referenced (absolute paths):

- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/structural/pipe_capacity/custom/PipeCapacity.py` — **CANONICAL solver**
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/structural/pipe_capacity/pipe_capacity.py` — **KEEP (orchestrator, distinct role)**
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/structural/pipe_capacity/common/pipe_components.py` — **KEEP (live routing through custom)**
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/engine.py` — caller, no edit needed (already points at orchestrator)
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/__init__.py` — caller, no edit needed (already points at orchestrator)
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/structural/pipe_capacity/PipeCapacity.py` — **DELETE (Phase 1)**
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/structural/pipe_capacity/common/PipeCapacity.py` — **DELETE (Phase 2, after test retarget)**
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/asset_integrity/custom/PipeCapacity.py` — **DELETE (Phase 3, after test retarget)**
- `/mnt/local-analysis/workspace-hub/digitalmodel/src/digitalmodel/asset_integrity/common/pipe_components.py` — **DELETE (Phase 3, 0 src/ callers)**
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/structural/pipe_capacity/test_pipe_capacity_custom.py` — **KEEP (108 tests against canonical)**
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/structural/pipe_capacity/test_pipe_capacity_common.py` — **RETARGET (Phase 2): point at `custom/PipeCapacity.py`, drop sys.path hack**
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/asset_integrity/test_calculations.py` — **RETARGET or DELETE (Phase 3)**
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/infrastructure/unit/test_pipe_capacity_codes.py` — **KEEP (7 tests against canonical)**
- `/mnt/local-analysis/workspace-hub/digitalmodel/tests/infrastructure/unit/test_pipe_capacity_dnv.py` — **KEEP (5 tests against canonical's `DNVWallThickness`)**
