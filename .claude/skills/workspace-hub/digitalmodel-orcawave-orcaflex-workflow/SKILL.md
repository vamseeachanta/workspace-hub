---
name: digitalmodel-orcawave-orcaflex-workflow
description: Current-state workflow for navigating and extending digitalmodel OrcaWave/OrcaFlex capabilities across code, tests, issues, queue tooling, and licensed-machine boundaries.
version: 2.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [digitalmodel, orcawave, orcaflex, diffraction, solver-queue, hydrodynamics, marine]
    related_skills: [engineering-solver-domain-recon, repo-capability-map, github-issues]
---

# digitalmodel OrcaWave / OrcaFlex Workflow

Use this skill when working on OrcaWave or OrcaFlex in the workspace-hub + digitalmodel ecosystem.

## Why this skill exists

The domain is large and split across multiple layers:
- package-level APIs (`src/digitalmodel/orcawave`, `src/digitalmodel/orcaflex`)
- deeper solver implementations (`src/digitalmodel/hydrodynamics/diffraction`, `src/digitalmodel/solvers/orcaflex`)
- queue tooling in workspace-hub (`scripts/solver/`)
- issue tracking in workspace-hub GitHub

Older docs often under-describe the true implementation surface. This skill gives the current operating map.

## First file to read

Start with:
- `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`

That file is the canonical navigation document for code, tests, issue clusters, and machine boundaries.

## Canonical code surface

### OrcaWave
1. `digitalmodel/src/digitalmodel/orcawave/`
   - public package API
   - RAO processing, wave spectra, hydro coefficients, panel mesh, motion statistics, drift forces, vessel database
2. `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/`
   - main diffraction implementation
   - `input_schemas.py` → `DiffractionSpec`
   - `orcawave_backend.py` → spec to native OrcaWave YAML
   - `reverse_parsers.py` → native AQWA/OrcaWave input back to spec
   - runners, comparators, benchmark tooling
3. `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/`
   - hull lookup, mesh generation, RAO database, catalog support
   - `rao_extractor.py` — xlsx → RAOData → RAODatabase pipeline (NEW April 2026)
   - `rao_database.py` — Parquet-backed RAODatabaseEntry store with query-by-parameter-range

### OrcaFlex
1. `digitalmodel/src/digitalmodel/orcaflex/`
   - public package API and reporting layer
   - model_builder, mooring_design, riser_config, weather window, postprocessor, VIV screening
2. `digitalmodel/src/digitalmodel/solvers/orcaflex/`
   - large solver-side implementation surface
   - modular generation, conversion, post-processing, browser, batch/parallel execution, mooring iteration, deeper integration helpers

### Licensed-machine fixture inventory (digitalmodel/tests/fixtures/solver/)
- `test01_unit_box.owr` + `.xlsx` — L00 case 2.1, 50 freqs, 2 headings (pipeline format)
- `ellipsoid.owr` + `.xlsx` — L00 case 2.8, 1 freq, 18 headings (pipeline format)
- `L00_test01.owr` + `.xlsx` — same as test01 but native OrcaWave export format
- `L01_001_ship_raos.owr` + `.xlsx` — ship RAOs, full QTF data (native format)
- `minimal_test.sim` + `.dat` — minimal OrcaFlex model (vessel + 1 mooring, 10s sim)
- `mooring_with_raos.sim` — OrcaFlex mooring model with RAO vessel (13.8 MB)
- `L02_OC4_semi_sub.owr` + `.xlsx` — OC4 semi-sub, 32 freqs, 9 headings (pipeline format, 546 KB)
- hemisphere.owr PERMANENTLY BLOCKED — HemisphereAndLid0814.gdf not found on licensed-win-1 (full-disk search confirmed absent; needs original WAMIT validation distribution)

### Queue / machine bridge
- `scripts/solver/process-queue.py`
- `scripts/solver/submit-job.sh`
- `scripts/solver/submit-batch.sh`
- `scripts/solver/watch-results.sh`
- `scripts/solver/post-process-hook.py`

## Issue clusters to inspect first

### Foundation
- `#1572` capability roadmap
- `#1628` phase plan

### OrcaWave maturity
- `#1638` reverse parser — CLOSED (implemented)
- `#1639` package coverage uplift — reporting tests done, diffraction benchmark gap remains
- `#1636` reporting section tests
- `#1606` damping sweep tests — CLOSED (stale issue, non-existent classes)

### Pipeline / handoff
- `#1588` parametric spec generator
- `#1592` OrcaWave to OrcaFlex handoff
- `#1597` RAO extractor to database
- `#1605` handoff integration test

### OrcaFlex maturity
- `#1652` real `.sim` integration test — needs licensed-win-1 fixture first
- `#1656` package maturity promotion — CLOSED (TESTED verdict, 1158 tests, 98% docstrings)
- `#1694` fatigue post-processing chain

### Engineering expansion
- `#1264` static frame analysis
- `#1292` dynamic parachute deployment
- `#1594` DLC matrix generator

## How to work the domain

### 1. Reconcile docs against source before planning
Do not trust narrow package docs alone. Inspect actual source directories and test directories.

### 2. Decide package-level vs solver-level change
- If the task is report API or reusable high-level utility → check `src/digitalmodel/orcawave` or `src/digitalmodel/orcaflex`
- If the task is solver conversion, full workflow, queue, or model generation → check `hydrodynamics/diffraction` or `solvers/orcaflex`

### 3. Use the smallest local test slice first
Examples:
- `uv run pytest digitalmodel/tests/orcawave/ -q`
- `uv run pytest digitalmodel/tests/hydrodynamics/diffraction/ -q`
- `uv run pytest digitalmodel/tests/orcaflex/ -q`
- `uv run pytest digitalmodel/tests/solvers/orcaflex/ -q`

Prefer focused test files before wider suites.

### 4. Respect the machine split

Can do locally on dev-primary:
- code changes
- schema changes
- generator logic
- mock-driven tests
- queue submission
- doc and issue alignment

Needs licensed validation when API/solver run is real:
- actual OrcaWave `.owr` generation
- actual OrcaFlex `.sim` generation
- live OrcFxAPI extraction against solver artifacts

### 5. Use the queue as the bridge
If real solver execution is needed, structure work so local code prepares inputs and post-processing while the licensed machine performs execution.

## The xlsx sidecar strategy (critical for dev-primary work)

.owr files are Orcina's proprietary binary format — they can ONLY be opened by OrcFxAPI
(requires commercial license on licensed-win-1). There is NO Python reader for .owr without OrcFxAPI.

The workaround: use .xlsx sidecar files as the license-free data bridge.
- `process-queue.py` on licensed-win-1 exports .xlsx alongside .owr at solve time
- dev-primary reads the .xlsx via `hull_library/rao_extractor.py` (openpyxl only)

Two xlsx formats exist — the extractor auto-detects:
1. **Pipeline format** (from process-queue.py `_export_orcawave_xlsx()`):
   - Sheets: Summary, RAOs, AddedMass, Damping, Discretization
   - RAOs columns: `{DOF}_Mag_H{heading}`, `{DOF}_Phase_H{heading}` — clean flat table
   - AddedMass/Damping columns: `{DOFi}_{DOFj}` for full 6x6 matrix

2. **Native format** (from OrcaWave GUI "Export to Spreadsheet"):
   - Sheets: Displacement RAOs, Added mass, Damping, Hydrostatics, Panel geometry, etc.
   - Displacement RAOs: heading value in **column 0**, frequency (rad/s) in **column 1**,
     then 12 data columns (amp, phase for each of 6 DOFs)
   - Added mass/Damping: per-frequency blocks with "frequency X.X rad/s" in column 1,
     then numbered row header (1-6), then 6x6 values

TRAP: The native format does NOT use "Heading = X deg" text markers — headings are
just numeric values in column 0 that change between blocks (e.g., 0.0 → 27.0).

## Two RAO data models (must bridge explicitly)

There are TWO different RAO representations in the codebase:
1. `RAOData` (hydrodynamics/models.py) — simple: frequencies, directions, amplitudes (n_freq, n_dir, 6), phases, vessel_name
2. `DiffractionResults` (diffraction/output_schemas.py) — complex: per-DOF RAOComponent + AddedMassSet + DampingSet + metadata

The RAO extractor produces RAOData. The OrcaFlexExporter consumes DiffractionResults.
Use `rao_data_to_diffraction_results()` from `diffraction/orcawave_to_orcaflex.py` to bridge.
(This was promoted from test code to production in the April 2026 session.)

TRAP: `DiffractionResults` requires non-None `added_mass` and `damping` fields (they're not Optional).
If you only have RAO data, you must zero-fill the matrix sets.

TRAP: `DiffractionResults` uses `source_files` (plural, List[str]) not `source_file` (singular).
`RAOSet` uses `source_file` (singular). Don't confuse them.

## Canonical handoff pipeline (April 2026)

The single-command automated pipeline:
```python
from digitalmodel.hydrodynamics.diffraction.orcawave_to_orcaflex import (
    convert_orcawave_xlsx_to_orcaflex,
)
outputs = convert_orcawave_xlsx_to_orcaflex("input.xlsx", "output/orcaflex")
```

CLI: `uv run python -m digitalmodel.hydrodynamics.diffraction.orcawave_to_orcaflex input.xlsx -o output/`

No OrcFxAPI needed. The post-process-hook.py auto-calls this for completed OrcaWave queue jobs.

Pipeline: rao_extractor → rao_data_to_diffraction_results → OrcaFlexExporter

## Known traps

1. `digitalmodel/README.md` historically referenced `specs/module-registry.yaml`, but that reference is stale unless the file is restored.
2. `digitalmodel/docs/domains/README.md` previously described outdated layout (`src/modules`, `tests/domains`). Use `src/digitalmodel/` and `tests/`.
3. Older roadmap text may describe queue scripts as missing even though they now exist.
4. The large implementation surface in `src/digitalmodel/solvers/orcaflex/` is easy to miss if you only inspect `src/digitalmodel/orcaflex/`.
5. The large implementation surface in `src/digitalmodel/hydrodynamics/diffraction/` is easy to miss if you only inspect `src/digitalmodel/orcawave/`.
6. Always use `uv run` for Python commands.
7. `solvers/orcawave/diffraction/scripts/convert_to_orcaflex.py` is a COMPLETELY SEPARATE pipeline from `diffraction/orcaflex_exporter.py` + `bemrosetta/converters/to_orcaflex.py`. It has its own VesselData model and never touches DiffractionResults. Don't confuse the two.
8. `solver/orcawave_converter.py` and `solver/orcawave_data_extraction.py` do hard `import OrcFxAPI` at module level — the entire solver/ subpackage fails to import without a license. Use try/except or mock for tests.
9. Hydrodynamic added mass/damping matrices are NOT symmetric — surge-pitch and sway-roll coupling terms differ by ~1-3%. Do not assert symmetry in tests.
10. **Rotational RAO unit mismatch**: OrcFxAPI and the pipeline-format xlsx store rotational DOFs (Roll, Pitch, Yaw) in **radians/m**. The benchmark hydro_data.yml and OrcaWave native xlsx store them in **degrees/m**. When comparing extracted vs benchmark data, multiply rotational DOFs by `180/π` before comparison. Without this, you get ~98% "error" that is purely a unit convention difference, not a data problem. Translational DOFs (Surge, Sway, Heave) are in m/m in both formats.
11. **OrcaFlex .dat and .sim files are BOTH binary** on this version (OrcaFlex 11.6). Neither is text-parseable without OrcFxAPI. Any dev-primary work involving .sim/.dat content must use the xlsx sidecar strategy or a licensed machine.

## Key metrics (April 2026 snapshot, updated 2026-04-04)

OrcaFlex public API package:
- TESTED maturity confirmed
- 22/22 modules have tests, 1158 test functions, 98% docstring coverage

OrcaWave + diffraction pipeline:
- ~85% file-level coverage after April 2026 uplift
- 1500+ test functions (incl. 506 new tests from April 3-4 sessions)
- Reporting subsystem fully covered (10 files, 166 tests)
- Report data models + computations covered (138 tests)
- Benchmark subsystem fully covered (11 files, 266 tests — #1784 CLOSED)
- CLI/exporter/batch/geometry now covered (#1785 CLOSED — 84 tests)
- Remaining gap: CLI entry points (cli.py, diffraction_cli.py), orcawave_test_utilities

xlsx-vs-owr validation (licensed-win-1 April 2026):
- Pipeline xlsx sidecar data is BIT-EXACT with OrcFxAPI .owr output
- test01_unit_box: freq diff 4.44e-16 rad/s, amplitude diff 0.0000%
- ellipsoid: all diffs exactly 0.00
- This means dev-primary pipeline work needs NO precision caveats — it matches the licensed solver

RAO extractor pipeline (#1765, #1597):
- IMPLEMENTED: `hull_library/rao_extractor.py` — 45 tests
- Reads .xlsx sidecars (no OrcFxAPI needed on dev-primary)
- Auto-detects pipeline vs native OrcaWave xlsx format
- Populates RAODatabase with Parquet persistence
- Bridge: `rao_data_to_diffraction_results()` converts RAOData → DiffractionResults

OrcaWave→OrcaFlex handoff validation (#1766, #1605):
- IMPLEMENTED: `test_orcawave_to_orcaflex_integration.py` — 33 tests
- Full round-trip: xlsx → RAOData → DiffractionResults → OrcaFlex export
- DOF-level validation: 1% amplitude, 5° phase tolerance
- Cross-format consistency: pipeline vs native xlsx agree

Parametric spec bridge (#1588):
- IMPLEMENTED: parametric_spec_generator.py (~310 lines) + 20 tests

Issue status (April 2026):
- #1656 CLOSED (TESTED maturity)
- #1638 CLOSED (already implemented with 33 round-trip tests)
- #1606 CLOSED (stale — referenced non-existent classes)
- #1597 CLOSED (full RAO extractor pipeline + database + comparison plots)
- #1592 CLOSED (automated handoff pipeline)
- #1605 CLOSED (handoff integration test)
- #1765 CLOSED (RAO extractor)
- #1766 CLOSED (handoff validation suite)
- #1768 CLOSED (automated pipeline + CLI)
- #1784 CLOSED (benchmark tests, 266 tests)
- #1785 CLOSED (CLI/exporter tests, 84 tests)
- #1786 CLOSED (RAO comparison plots)
- #1787 CLOSED (RAODatabase auto-population)
- #1572 CLOSED (domain capability roadmaps)
- #1652 OPEN (blocked on licensed-win-1 for .sim metadata extraction → #1827)
- #1788 OPEN (blocked on licensed-win-1 → #1827)
- #1789 OPEN (hemisphere .gdf blocked/backlog — file not found anywhere)
- #1768 DONE (automated handoff pipeline + CLI + post-process-hook integration, commit 23275916)
- #1786 CLOSED (RAO comparison plots — <0.06% on all significant DOFs, rad→deg fix for rotational)
- #1787 CLOSED (RAODatabase auto-population from queue, query CLI)
- #1597 CLOSED (all deliverables: extractor, plots, auto-population, validation)
- Licensed-machine prompts: docs/plans/licensed-win-1-session-3-prompts.md
- Session 1: licensed-win-1 completed prompts 1-4; hemisphere.owr failed (missing .gdf)
- Session 2: Prompt 2 (xlsx-vs-owr validation) completed — ALL PASS at machine-epsilon.
- Session 3: L02 fixture committed, pipeline validated on OrcaFlex, validation extended to 3 geometries. Hemisphere confirmed permanently blocked.
- #1785 CLOSED (CLI/exporter tests — 84 tests, commit bfaf228b)
- validate_xlsx_against_owr.py committed to scripts/solver/ for future re-runs

## Good completion criteria

A good OrcaWave/OrcaFlex task is not complete until you also:
1. update the operator map if navigation changed
2. update or reconcile the related GitHub issue(s)
3. note whether the change is local-only or requires licensed-machine validation
4. align stale docs if you discovered drift

## Traceability loop for documentation and mapping work

When you create or materially improve a domain map, workflow doc, or reusable skill for this area:
1. create GitHub issues for traceability if the work is substantial enough to matter later
2. comment on the parent roadmap/tracking issue with the new artifact paths
3. include issue numbers back in the operator map or roadmap note so future readers can follow provenance
4. commit and push the map/roadmap changes immediately to avoid losing the navigation improvements

This is especially useful when the work is documentation-heavy rather than feature-code-heavy; otherwise the repo gains knowledge but loses auditability.

## Recommended output artifacts after significant work

- doc update: `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`
- detailed reconciliation report when backlog reality is unclear: `docs/reports/digitalmodel-orcawave-orcaflex-issue-reconciliation.md`
- issue reconciliation notes inside the operator map
- linked GH issue(s) for traceability
- comments on partially stale issues to re-scope them from greenfield build to validation / hardening when appropriate
- if solver-facing: explicit note on local vs licensed validation status

## GTM-oriented framing rule

When the user is building future GTM positioning from this domain, classify findings into three buckets:
1. Can position now — capabilities already backed by real code, tests, docs, or queue tooling
2. Needs evidence — capabilities that exist architecturally but still need real fixtures, end-to-end validation, or benchmark-quality proof
3. Real future gap — capabilities that still require substantive engineering implementation

Do not let GTM planning inherit stale issue language. Reconcile issue text against current repo state first, then produce a sharper narrative around already-built capability vs validation debt vs true future work.
