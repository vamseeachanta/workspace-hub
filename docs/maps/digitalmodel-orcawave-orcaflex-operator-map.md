# digitalmodel OrcaWave / OrcaFlex Operator Map

Updated: 2026-04-02
Purpose: canonical navigation map for future OrcaWave/OrcaFlex work across digitalmodel and workspace-hub.
Traceability: #1752 operator map, #1753 stale-doc repairs, #1754 reusable workflow skill.

Related detailed reconciliation report: `docs/reports/digitalmodel-orcawave-orcaflex-issue-reconciliation.md`.

## 1. What this map is for

Use this document before touching OrcaWave or OrcaFlex code. It is the current-state operator guide linking:
- code locations
- test locations
- issue clusters
- supporting docs
- machine boundaries
- known documentation drift

This map supersedes older narrower views that focused only on the small reporting packages.

## 2. Canonical code surface

### OrcaWave core
1. `digitalmodel/src/digitalmodel/orcawave/`
   - package-level utilities and reporting-facing API
   - wave spectra, RAO processing, hydro coefficients, panel mesh, motion statistics, drift forces, vessel database
2. `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/`
   - primary diffraction pipeline and solver-facing implementation
   - `input_schemas.py` — canonical `DiffractionSpec`
   - `orcawave_backend.py` — spec to native OrcaWave YAML
   - `reverse_parsers.py` — native input back to `DiffractionSpec`
   - `orcawave_runner.py`, `orcawave_batch_runner.py`
   - `comparison_framework.py`, `benchmark_runner.py`, `result_extractor.py`
3. `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/`
   - hull parameterization, mesh generation, lookup, RAO database, catalog support

### OrcaFlex core
1. `digitalmodel/src/digitalmodel/orcaflex/`
   - public package entry point and report-generation API
   - environment, model_builder, mooring_design, riser_config, pipelay_analysis, installation_analysis, weather_window, VIV screening, postprocessor
2. `digitalmodel/src/digitalmodel/solvers/orcaflex/`
   - largest implementation surface
   - model generation, conversion, post-processing, modular generator, mooring tension iteration, browser utilities, batch/parallel execution, reporting, integration helpers
3. `digitalmodel/src/digitalmodel/subsea/mooring_analysis/`
   - supporting mooring workflows and generation helpers

### Cross-domain bridge
1. `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcawave_to_orcaflex.py` — **canonical single-command pipeline** (xlsx → RAOData → DiffractionResults → OrcaFlex YAML/CSV)
2. `digitalmodel/src/digitalmodel/hydrodynamics/diffraction/orcaflex_exporter.py` — export engine (DiffractionResults → OrcaFlex files)
3. `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/rao_extractor.py` — xlsx → RAOData + HydroCoefficients extraction
4. `digitalmodel/src/digitalmodel/marine_ops/marine_analysis/unified_rao_reader.py`
5. `digitalmodel/src/digitalmodel/hydrodynamics/bemrosetta/converters/to_orcaflex.py`
6. `digitalmodel/src/digitalmodel/solvers/orcawave/diffraction/scripts/convert_to_orcaflex.py` (legacy parallel implementation)

### Solver queue / machine handoff
1. `scripts/solver/process-queue.py`
2. `scripts/solver/submit-job.sh`
3. `scripts/solver/submit-batch.sh`
4. `scripts/solver/watch-results.sh`
5. `scripts/solver/post-process-hook.py`

## 3. Tests that matter first

### OrcaWave
- `digitalmodel/tests/orcawave/`
- `digitalmodel/tests/hydrodynamics/diffraction/`
- `digitalmodel/tests/workflows/orcawave/`
- `digitalmodel/tests/solvers/orcawave/`

### OrcaFlex
- `digitalmodel/tests/orcaflex/`
- `digitalmodel/tests/solvers/orcaflex/`
- `digitalmodel/tests/workflows/agents/orcaflex/`
- `digitalmodel/tests/signal_processing/signal_analysis/test_orcaflex_tension_analysis.py`

### Key current scale snapshot
- `src/digitalmodel/solvers/orcaflex/`: 259 Python files, ~58.5k LOC
- `src/digitalmodel/hydrodynamics/diffraction/`: 55 Python files, ~21.9k LOC
- `src/digitalmodel/orcaflex/`: 25 Python files
- `src/digitalmodel/orcawave/`: 20 Python files

## 4. Capability clusters

### A. DiffractionSpec pipeline
Primary files:
- `hydrodynamics/diffraction/input_schemas.py`
- `hydrodynamics/diffraction/spec_converter.py`
- `hydrodynamics/diffraction/orcawave_backend.py`
- `hydrodynamics/diffraction/reverse_parsers.py`

Focus issues:
- #1638 reverse parser tests / completion
- #1588 parametric spec generation
- #1598 end-to-end pipeline integration

### B. RAO extraction and storage
Primary files:
- `hydrodynamics/diffraction/result_extractor.py`
- `hydrodynamics/hull_library/rao_database.py`
- `marine_ops/marine_analysis/unified_rao_reader.py`

Focus issues:
- #1597 RAO extractor and DB population
- #1605 OrcaWave to OrcaFlex integration validation

### C. OrcaWave reporting and package maturity
Primary files:
- `src/digitalmodel/orcawave/reporting/`
- supporting package modules under `src/digitalmodel/orcawave/`

Focus issues:
- #1639 coverage uplift to TESTED
- #1636 reporting section-level unit tests
- #1606 damping sweep tests

### D. OrcaFlex reporting and package maturity
Primary files:
- `src/digitalmodel/orcaflex/reporting/`
- public package modules under `src/digitalmodel/orcaflex/`
- deeper integrations in `src/digitalmodel/solvers/orcaflex/`

Focus issues:
- #1652 real `.sim` integration test + HTML snapshot testing
- #1656 maturity promotion after test uplift
- #1694 fatigue post-processing chain

### E. OrcaWave to OrcaFlex handoff
Primary files:
- `hydrodynamics/diffraction/orcaflex_exporter.py`
- `bemrosetta/converters/to_orcaflex.py`
- `solvers/orcawave/diffraction/scripts/convert_to_orcaflex.py`

Focus issues:
- #1592 automate handoff
- #1605 validate end-to-end import/export

### F. Engineering templates / project workflows
Primary files:
- `src/digitalmodel/solvers/orcaflex/modular_generator/`
- `src/digitalmodel/workflows/agents/orcaflex/`
- `docs/domains/orcaflex/`

Focus issues:
- #1264 static frame analysis
- #1292 parachute deployment dynamic analysis
- #1594 DLC matrix generator

## 5. Supporting docs to trust first

### Current best docs
- `docs/roadmaps/orcawave-orcaflex-capability-roadmap.md`
- `docs/reports/orcawave-orcaflex-research-gaps.md`
- `docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md`
- `digitalmodel/ROADMAP.md`
- `digitalmodel/docs/domains/orcaflex/`
- `digitalmodel/docs/domains/orcawave/`

### Important caveat
The roadmap and plan docs are useful but partially stale. They under-describe the full implementation already present in:
- `src/digitalmodel/solvers/orcaflex/`
- `src/digitalmodel/hydrodynamics/diffraction/`

Always reconcile documentation claims against current source and tests.

## 6. Known documentation drift / traps

1. `digitalmodel/README.md` references `specs/module-registry.yaml`, but that file is not present.
2. `digitalmodel/docs/domains/README.md` still describes an older source/test layout (`src/modules`, `tests/domains`).
3. Older roadmap text may describe queue tooling as missing even though these now exist:
   - `submit-batch.sh`
   - `watch-results.sh`
   - `post-process-hook.py`
4. Narrow package docs can mislead operators into ignoring the larger solver surfaces.

## 7. Machine boundary

### Can do on dev-primary
- schema and generator work
- package and solver-side Python implementation
- unit and mock-driven integration tests
- batch manifest creation
- queue submission
- result post-processing that does not require live licensed APIs
- roadmap, skill, and documentation updates

### Must be validated on licensed machine when license/API is required
- real OrcaWave runs (`.owd` / native YAML to `.owr`)
- real OrcaFlex runs (`.dat` / `.yml` to `.sim`)
- live OrcFxAPI-dependent extraction against actual solver artifacts

### Bridge
Use the git-based solver queue under `scripts/solver/` and `queue/`.

## 8. Recommended execution order for future work

1. Reconcile open issues against current code and mark stale-vs-real gaps.
2. Use package tests for fast local confidence, then solver-level tests.
3. For OrcaWave pipeline work, start with `DiffractionSpec` and `hydrodynamics/diffraction/`.
4. For OrcaFlex workflow work, inspect both `src/digitalmodel/orcaflex/` and `src/digitalmodel/solvers/orcaflex/` before planning changes.
5. For handoff work, always include validation of units, coordinates, headings, and frequency conventions.
6. After code changes, update this map and the relevant issue cluster summary.

## 9. High-value issue clusters to keep active

- Foundation / planning:
  - #1572 capability roadmap
  - #1628 sprint plan
- OrcaWave maturity:
  - #1638, #1639, #1636, #1606
- Pipeline / integration:
  - #1588, #1592, #1597, #1605
- OrcaFlex maturity:
  - #1652, #1656, #1694
- Engineering expansion:
  - #1264, #1292, #1594

## 9A. Issue reconciliation snapshot

This snapshot reflects the repo state observed during the April 2026 review.

### Already represented in code and docs enough to treat as partial/advanced
- #1572 roadmap exists and is useful, but should not be treated as the sole navigation artifact
- #1586 / #1595 queue tooling is no longer just planned; `submit-batch.sh`, `watch-results.sh`, and `post-process-hook.py` now exist
- #1638 reverse parser capability exists in code and needs validation/test-strengthening rather than greenfield implementation
- #1639 and #1656 are maturity/coverage promotion issues, not blank-slate feature issues

### Still real gaps worth active follow-through
- #1597 RAO extractor to RAODatabase population
- #1592 and #1605 OrcaWave to OrcaFlex handoff automation and integration validation
- #1652 real `.sim` integration fixture and snapshot testing
- #1264 and #1292 engineering analysis templates for static and dynamic frame/parachute workflows

### Operating rule
When starting from an old issue body, reconcile it against current source before planning implementation.

## 10. Operator checklist

Before starting new work:
1. Read this map.
2. Read the relevant issue body.
3. Inspect actual source directories, not just package-level `__init__.py`.
4. Confirm whether the task is local-only or licensed-machine dependent.
5. Run the smallest relevant local test slice first.
6. Update docs and issue mapping when done.
