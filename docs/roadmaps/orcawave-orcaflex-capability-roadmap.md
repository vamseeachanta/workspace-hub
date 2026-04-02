# OrcaWave/OrcaFlex Domain Capability Roadmap

> Generated: 2026-04-01 | Issue: #1572 | Cross-reference: docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md

## Scale Summary

| Domain | Skills | Code Modules | LOC | Test Files | Open Issues |
|--------|--------|-------------|-----|-----------|-------------|
| OrcaWave (diffraction) | 8 skills | 55 modules | 21,904 | 38 | 9 |
| OrcaWave (reporting) | (included above) | 13 modules | 1,033 | — | — |
| OrcaFlex (solver) | 24 skills | 259 modules | 58,416 | 101 | 14 |
| OrcaFlex (reporting) | (included above) | 14 modules | (above) | — | — |
| Hull Library | — | 25 modules | ~8,100 | 34 | 4 |
| Parametric Hull Analysis | — | 8 modules | ~2,000 | 1 | 2 |
| **Total** | **32 skills** | **374 modules** | **~91,500** | **174** | **29** |

---

## 1. OrcaWave Capabilities

### 1.1 Skills Inventory

| Skill | Type | Description |
|-------|------|-------------|
| `orcawave/` (root) | domain | Root skill linking all sub-skills |
| `orcawave/analysis/` | reference | Expert agent for diffraction/radiation: wave-structure interaction, added mass/damping, QTF, hydrodynamic database generation |
| `orcawave/aqwa-benchmark/` | reference | Cross-validation: OrcaWave vs AQWA. Statistical comparison, peak validation, automated benchmark reporting |
| `orcawave/damping-sweep/` | reference | Viscous damping parametric studies: roll damping, critical damping, bilge keel effects, model test comparison |
| `orcawave/mesh-generation/` | reference | Panel mesh generation: CAD/STL→GDF, convergence studies, waterline refinement, mesh quality validation |
| `orcawave/multi-body/` | reference | Multi-body interactions: side-by-side, FPSO-tanker, gap resonance, hydrodynamic shielding |
| `orcawave/qtf-analysis/` | reference | Second-order QTFs: mean drift, difference/sum frequency, slow drift, Newman approximation |
| `orcawave/to-orcaflex/` | reference | OrcaWave→OrcaFlex: hydrodynamic database, RAO import, viscous damping, coordinate transforms |

### 1.2 Code Module Map

#### Core Pipeline: `hydrodynamics/diffraction/` (55 modules, 21,904 LOC)

| Module | Lines | Purpose | Tests? |
|--------|-------|---------|--------|
| **input_schemas.py** | 789 | DiffractionSpec Pydantic v2 — spec.yml validation, unit conversion | test_input_schemas.py |
| **orcawave_backend.py** | — | DiffractionSpec → OrcaWave native YAML conversion | test_orcawave_backend.py |
| **orcawave_runner.py** | — | OrcaWave API execution wrapper | test_orcawave_runner.py |
| **orcawave_batch_runner.py** | — | Batch execution of multiple OrcaWave runs | test_orcawave_batch_runner.py |
| **orcawave_test_utilities.py** | — | Test helpers for OrcaWave validation | — |
| **aqwa_backend.py** | — | DiffractionSpec → AQWA input conversion | test_aqwa_backend.py |
| **aqwa_runner.py** | — | AQWA execution wrapper | test_aqwa_runner.py |
| **aqwa_batch_runner.py** | — | Batch AQWA execution | test_aqwa_batch_runner.py |
| **aqwa_ah1_parser.py** | — | AQWA .AH1 file parser | test_aqwa_ah1_parser.py |
| **aqwa_lis_parser.py** | — | AQWA .LIS results parser | — |
| **aqwa_converter.py** | — | AQWA format conversion utilities | — |
| **aqwa_result_extractor.py** | — | Extract results from AQWA output | test_aqwa_result_extractor.py |
| **batch_processor.py** | — | Generic batch processing framework | — |
| **benchmark_runner.py** | — | Cross-solver benchmark orchestration | test_benchmark_runner.py |
| **benchmark_plotter.py** | — | Benchmark RAO comparison plots | test_benchmark_plotter.py |
| **benchmark_correlation.py** | — | Statistical correlation metrics | — |
| **benchmark_dof_sections.py** | — | Per-DOF benchmark sections | — |
| **benchmark_dof_tables.py** | — | Tabular DOF comparisons | — |
| **benchmark_helpers.py** | — | Benchmark utility functions | — |
| **benchmark_input_comparison.py** | — | Input file diff | — |
| **benchmark_input_files.py** | — | Input file management | — |
| **benchmark_input_reports.py** | — | Input comparison reports | — |
| **benchmark_mesh_schematic.py** | — | Mesh visualization for benchmarks | — |
| **benchmark_rao_helpers.py** | — | RAO extraction for benchmarks | — |
| **benchmark_rao_plots.py** | — | RAO comparison plots | — |
| **benchmark_rao_summary.py** | — | Summary statistics | — |
| **comparison_framework.py** | — | Multi-solver comparison | — |
| **multi_solver_comparator.py** | — | Side-by-side solver comparison | test_multi_solver_comparator.py |
| **cli.py** | — | CLI entry point | test_cli_integration.py |
| **diffraction_cli.py** | — | Diffraction-specific CLI | — |
| **diffraction_units.py** | — | Unit conversion utilities | test_diffraction_units.py |
| **geometry_quality.py** | — | Mesh quality assessment | — |
| **gmsh_mesh_builder.py** | — | GMSH-based mesh generation | test_gmsh_mesh_builder.py |
| **mesh_pipeline.py** | — | End-to-end mesh processing | test_mesh_pipeline.py |
| **orcaflex_exporter.py** | — | Export to OrcaFlex format | — |
| **output_schemas.py** | — | Result data models | — |
| **output_validator.py** | — | Result validation | test_output_validator_resonance.py |
| **polars_exporter.py** | — | Polars DataFrame export | test_polars_exporter.py |
| **rao_plotter.py** | — | RAO visualization | test_rao_plotter.py |
| **report_builders.py** | — | Report section builders | — |
| **report_builders_header.py** | — | Report header generation | — |
| **report_builders_hydrostatics.py** | — | Hydrostatics report sections | — |
| **report_builders_responses.py** | — | Response report sections | — |
| **report_computations.py** | — | Derived quantities | — |
| **report_data_models.py** | — | Report data models | — |
| **report_generator.py** | — | Full report generation | test_report_generator.py |
| **result_extractor.py** | — | Generic result extraction | test_result_extractor.py |
| **reverse_parsers.py** | — | OrcaWave output parsers | test_reverse_parsers.py |
| **spec_converter.py** | — | Spec format conversion | — |
| **wamit_reference_loader.py** | — | WAMIT reference data loading | — |
| **solver/orcawave_converter.py** | — | Native OrcaWave conversion | — |
| **solver/orcawave_data_extraction.py** | — | Data extraction from OrcaWave | — |
| **solver/report_extractors.py** | — | Report extraction | — |

#### OrcaWave Reporting: `orcawave/reporting/` (13 modules, 1,033 LOC)

| Module | Purpose |
|--------|---------|
| `builder.py` | Report builder |
| `config.py` | Report configuration |
| `sections/rao_plots.py` | RAO plot sections |
| `sections/hydro_matrices.py` | Added mass/damping matrix sections |
| `sections/mean_drift.py` | Mean drift force sections |
| `sections/multi_body.py` | Multi-body interaction sections |
| `sections/panel_pressures.py` | Panel pressure visualization |
| `sections/qa_summary.py` | QA summary sections |
| `sections/qtf_heatmap.py` | QTF heatmap visualization |
| `sections/model_summary.py` | Model overview sections |

### 1.3 DiffractionSpec Pipeline (Core Workflow)

```
spec.yml (20-30 lines, human/LLM authored)
    ↓ DiffractionSpec.from_yaml()  [input_schemas.py — 789 lines Pydantic v2]
    ↓ Validates: vessel, environment, frequencies, headings, solver options
    ↓ Unit conversion: kg→te, kg/m³→te/m³ for OrcaFlex-SI
    ↓
OrcaWaveBackend.convert()  [orcawave_backend.py]
    ↓ Generates: OrcaWave native YAML (~180 lines, %YAML 1.1 header)
    ↓ Resolves: mesh paths, frequency lists, inertia tensors
    ↓
submit-job.sh → queue/ → licensed-win-1 polls → OrcFxAPI execution
    ↓
.owr result → result_extractor.py → RAOs, added mass, damping
    ↓
report_generator.py → HTML/PDF engineering report
```

**13 live spec.yml files** validated against this pipeline (L00 WAMIT validation × 10, L02 barge, L03 ship, L04 spar).

### 1.4 Skill → Code → Test → Issue Mapping

| Skill | Primary Code Modules | Tests | Open Issues |
|-------|---------------------|-------|-------------|
| analysis | input_schemas.py, orcawave_backend.py, orcawave_runner.py | 3 test files | #22 (parametric RAO), #29 (Unit Box benchmark) |
| aqwa-benchmark | aqwa_backend.py, benchmark_runner.py, comparison_framework.py | 6 test files | #21 (SPM AQWA vs OrcaFlex) |
| damping-sweep | (no dedicated module — part of input_schemas.py solver_options) | — | — |
| mesh-generation | gmsh_mesh_builder.py, mesh_pipeline.py, geometry_quality.py + hull_library/ | 2 test files | — |
| multi-body | input_schemas.py (bodies[] array), orcawave_backend.py | via test_input_schemas.py | — |
| qtf-analysis | input_schemas.py (analysis_type: full_qtf), output_schemas.py | — | — |
| to-orcaflex | orcaflex_exporter.py, spec_converter.py | — | — |

---

## 2. OrcaFlex Capabilities

### 2.1 Skills Inventory (24 Skills)

| Skill | Description |
|-------|-------------|
| `orcaflex/` (root) | Root: modeling, analysis, post-processing, validation |
| `batch-manager/` | Large-scale batch processing with parallel execution |
| `code-check/` | Verify results against industry standards (DNV, API, ISO) |
| `environment-config/` | Environmental conditions: JONSWAP, PM, current profiles |
| `extreme-analysis/` | Extreme response extraction with linked statistics |
| `file-conversion/` | Format conversion: .dat ↔ .yml ↔ .sim |
| `installation-analysis/` | Offshore installation sequence modeling |
| `jumper-analysis/` | Rigid/flexible jumper: installation, in-place, VIV, fatigue |
| `line-wizard/` | Line Setup Wizard: properties, segment types |
| `modal-analysis/` | Natural frequencies and mode shapes |
| `model-generator/` | Generate modular models from spec.yml (builder registry) |
| `modeling/` | General setup, configuration, and execution |
| `model-sanitization/` | Strip client data, convert binary→YAML, organize library |
| `monolithic-to-modular/` | Convert monolithic .dat/.yml to spec-driven modular |
| `mooring-iteration/` | Iterate line lengths for target pretensions (scipy) |
| `operability/` | Multi-sea-state operability assessment |
| `post-processing/` | OPP (OrcaFlex Post-Process) framework |
| `rao-import/` | Import RAOs from external sources (OrcaWave, AQWA) |
| `results-comparison/` | Cross-simulation comparison for design verification |
| `spec-audit/` | Audit/classify/score spec.yml quality |
| `specialist/` | Python API automation: mooring, riser, pipeline |
| `static-debug/` | Static analysis convergence troubleshooting |
| `vessel-setup/` | 6-DOF vessel configuration with hydrodynamic properties |
| `visualization/` | OrcaFlex/OrcaWave simulation visualization |
| `yaml-gotchas/` | Production-proven YAML traps and solutions |

### 2.2 Code Module Map

#### Core Solver: `solvers/orcaflex/` (259 modules, 58,416 LOC)

**Sub-packages and their scope:**

| Sub-Package | Modules | Purpose |
|-------------|---------|---------|
| `core/` | 10 | Base classes, configuration, registry, model interface, exceptions, logging |
| `modular_generator/` | 30+ | Spec-driven model generation: builders (vessel, mooring, riser, environment, lines, etc.), routers (vessel, mooring), schema (campaign, equipment, simulation, riser, mooring, pipeline) |
| `modular_input_validation/` | 12 | 3-level validation: L1 YAML syntax, L2 OrcaFlex compatibility, L3 physical checks |
| `mooring_analysis/` | 14 | Comprehensive mooring: pretension, stiffness, fender forces, natural periods, group comparison, visualization |
| `mooring_tension_iteration/` | 5 | Line length iteration for target pretension via scipy |
| `format_converter/` | 10 | Bidirectional: single↔modular↔spec format conversion |
| `analysis/` | 4 | Analysis engine: CLI, comparative, report generation |
| `reporting/` | 40+ | Full engineering reports: extractors (geometry, BC, loads, materials, mesh, mooring, results), models (analysis, BC, design checks, fatigue, geometry, loads, materials, mesh, results), renderers (installation, jumper, mooring, pipeline, riser), section builders (15+) |
| `examples_integration/` | 12 | Download, convert, analyze OrcaFlex example models |
| `browser/` | 3 | Web-based OrcaFlex data viewer |
| `universal/` | 6 | Universal runner: model discovery, batch processing, status reporting |
| `post_process/` | 2 | Post-processing pipeline |
| `post_results/` | 8 | Legacy post-processing (ASCII→DataFrame, fatigue, plotting) |
| `utils/` | 2 | Validation utilities |
| Top-level modules | 40+ | OrcaFlex analysis, parallel execution (3 versions), fatigue, modal, installation, operability, time series processing, visualization, file optimization, template generation, etc. |

#### OrcaFlex Reporting: `orcaflex/reporting/` (14 modules)

| Module | Purpose |
|--------|---------|
| `sections/code_check.py` | Design code check sections |
| `sections/modal_analysis.py` | Modal results |
| `sections/model_summary.py` | Model overview |
| `sections/mooring_loads.py` | Mooring load summary |
| `sections/qa_summary.py` | QA results |
| `sections/range_graphs.py` | Range graph sections |
| `sections/static_config.py` | Static configuration |
| `sections/time_series.py` | Time series plots |
| `qa.py` | QA framework |

### 2.3 Solver Queue Pipeline

```
scripts/solver/submit-job.sh
    ↓ Creates job YAML in queue/pending/
    ↓ git commit + push
    ↓
licensed-win-1 polls (Task Scheduler, every 30 min)
    ↓ scripts/solver/process-queue.py
    ↓ Runs OrcFxAPI (OrcaWave or OrcaFlex)
    ↓
queue/completed/{job-id}/result.yaml
    ↓ git commit + push from licensed-win-1
```

**Status:** 1 completed run (test01.owd, 7.8s), 1 failed (path error). Batch submission not yet built. No auto post-processing.

### 2.4 dat-to-yaml Enrichment Pipeline

```
scripts/data/orcaflex/
├── dat-to-yaml.py      # Convert binary .dat → human-readable .yml
├── enrich-and-clean.py  # Sanitize, annotate, standardize YAML
├── README.md            # Pipeline documentation
└── _archive/anonymize-import.py  # Client data removal
```

### 2.5 Skill → Code → Test → Issue Mapping (OrcaFlex)

| Skill | Primary Code Modules | Tests | Open Issues |
|-------|---------------------|-------|-------------|
| model-generator | modular_generator/ (30+ modules) | 15+ test files | #19 (modular pipeline) |
| mooring-iteration | mooring_tension_iteration/ (5 modules) | — | — |
| jumper-analysis | orcaflex_analysis.py, orcaflex_custom_analysis.py | — | #23 (rigid jumper) |
| installation-analysis | orcaflex_installation.py, umbilical_* | — | #20 (deployment) |
| file-conversion | format_converter/ (10 modules) | 7 test files | — |
| code-check | reporting/models/design_checks.py | — | — |
| batch-manager | universal/ (6 modules) | — | — |
| post-processing | opp*.py (7 modules), post_process/ | — | — |
| modal-analysis | orcaflex_modal_analysis.py | — | — |
| extreme-analysis | opp_linkedstatistics.py | — | — |
| operability | operability_analysis.py | — | — |
| specialist | orcaflex.py, orcaflex_utilities.py | — | #24 (riser parametric) |
| vessel-setup | preprocess/load_vessel.py | test_load_vessel_aqwa.py | — |
| modeling | core/ (10 modules) | — | — |
| rao-import | (linked to OrcaWave to-orcaflex) | — | — |
| visualization | visualization.py, pipeline_schematic.py | — | — |
| spec-audit | (uses modular_input_validation/) | — | — |
| static-debug | (diagnostic, no dedicated module) | — | — |
| yaml-gotchas | (reference skill, no code) | — | — |

---

## 3. Open GitHub Issues

### OrcaWave/Diffraction Issues

| # | Title | Priority | Status |
|---|-------|----------|--------|
| #22 | WRK-043: Parametric hull form analysis with RAO generation | low | Open — parent issue for hull_library |
| #29 | WRK-099: Run 3-way benchmark on Unit Box hull | medium | Open — needs solver queue |
| #21 | WRK-039: SPM project benchmarking - AQWA vs OrcaFlex | medium | Open |
| #1464 | Capytaine BEM available for hull mesh wave load analysis | low | Open |
| #1440 | Install Capytaine BEM solver into ACE ecosystem | — | Open |
| #1314 | WRK-1372: Ship-specific hydrostatic data tables (DDG-51, FFG-7) | — | Open |
| #1319 | WRK-1377: Hull form parametric design — Series 60 | — | Open |
| #1291 | WRK-1339: Deepen naval architecture knowledge from SNAME | high | Open |
| #1297 | WRK-1382: Naval architect expert skill | high | Open |

### OrcaFlex Issues

| # | Title | Priority | Status |
|---|-------|----------|--------|
| #1264 | WRK-1365: OrcaFlex frame analysis (static) | high | Open — parachute frame |
| #1292 | WRK-1342: OrcaFlex parachute deployment (dynamic snap loads) | medium | Open |
| #1242 | WRK-5082: Parachute frame force calculation (parent) | — | Open |
| #1265 | WRK-1366: 2D vs 3D comparison | — | Open |
| #1267 | WRK-1368: Pipeline and engineering report | — | Open |
| #19 | WRK-032: Modular OrcaFlex pipeline installation input | medium | Open |
| #24 | WRK-046: OrcaFlex drilling/completion riser parametric | medium | Open |
| #23 | WRK-045: OrcaFlex rigid jumper analysis | low | Open |
| #20 | WRK-036: OrcaFlex structure deployment (supply boat) | low | Open |
| #28 | WRK-075: OFFPIPE integration — pipelay cross-validation | low | Open |

### Cross-Domain Issues

| # | Title | Priority | Status |
|---|-------|----------|--------|
| #1572 | Domain-specific capability roadmaps | high | Open — this deliverable |
| #1567 | Continuous Repo Architecture Intelligence | high | Open — parent |
| #1360 | Extract algorithms from riser-eng-job archives | — | Open |
| #1363 | LLM domain-tag riser-eng-job literature | — | Open |
| #25 | WRK-047: OpenFOAM CFD analysis capability | low | Open |
| #14 | WRK-1251: FreeCAD parametric engineering | medium | Open |
| #1268 | WRK-5095: CFD car+parachute aerodynamics | — | Open |
| #1444 | Integrate RAFT floating wind turbine | high | Open |
| #1460 | Integrate WEIS floating wind co-design | medium | Open |

---

## 4. Gap Analysis: What's NOT Yet Automated

### OrcaWave Gaps

1. **No automated end-to-end pipeline** — spec.yml generation, submission, execution, result extraction, and reporting are all manual steps that could be chained.

2. **Parametric spec.yml generator missing** — Can't yet go from "sweep 5 hull lengths × 3 drafts" to "15 validated spec.yml files" automatically. The DiffractionSpec schema validates but doesn't generate.

3. **No OrcaWave result parser on dev-primary** — Result extraction requires OrcFxAPI on licensed-win-1. No mechanism to extract RAOs from .owr files without the license.

4. **WAMIT validation not automated** — 10 L00 spec.yml files exist but no automated validation runner that compares OrcaWave results against WAMIT reference data.

5. **Capytaine integration incomplete** — Issues #1440 and #1464 are open. sweep.py references Capytaine but no proof of operational runs.

6. **QTF post-processing thin** — qtf_heatmap.py exists in reporting but no automated QTF-specific analysis workflow.

7. **Damping sweep has no dedicated code** — Skill exists but maps to solver_options in input_schemas.py. No automated damping coefficient optimization.

### OrcaFlex Gaps

1. **Solver queue not hardened** — Only 1 successful run. No batch submission, no auto post-processing, no result watching.

2. **Mooring iteration not integrated with solver queue** — mooring_tension_iteration/ exists but requires live OrcFxAPI (can't run on dev-primary).

3. **No installation analysis templates** — Skill and code exist but no example spec.yml for installation sequences.

4. **Fatigue analysis incomplete** — orcaflex_fatigue_analysis.py exists but no SN curve library integration or standard-specific fatigue checkers.

5. **No production VIV analysis** — Mentioned in jumper-analysis skill but no dedicated VIV module.

6. **Engineering report automation partial** — Extensive reporting infrastructure (40+ modules) but no one-command "generate full report from simulation results."

7. **Model library not populated** — format_converter and model_sanitization work but the actual library of reference models is sparse.

### Cross-Domain Gaps

1. **No unified workflow orchestrator** — OrcaWave→OrcaFlex handoff is manual. Need: spec.yml → OrcaWave → RAOs → OrcaFlex vessel type → time-domain simulation → report.

2. **Hull library → DiffractionSpec bridge** — hull_library generates meshes and hull profiles, but no automated path to generate DiffractionSpec-compliant spec.yml from a hull catalog entry.

3. **No design load case matrix** — Individual analyses work but no systematic DLC (Design Load Case) generation for standard compliance (e.g., DNV-OS-E301 mooring DLCs).

4. **Riser engineering module thin** — #1360 (extract riser algorithms) and #1363 (tag riser literature) are prerequisites. The solvers/orcaflex has riser builders but no riser design workflow.

5. **No CFD coupling** — #25 (OpenFOAM) and #1268 (car+parachute CFD) are open but no code exists.

---

## 5. Cross-Reference with Intensive Plan

### Plan Reference: docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md

| Wave | Plan Task | Current Status | Gap |
|------|----------|----------------|-----|
| Wave 1 | Solver queue hardening | 1 run complete, batch not built | Need batch submission, result watcher |
| Wave 1 | Licensed-win-1 sync | Polling active, 1 completed job | Need health monitoring |
| Wave 2 | Hull library audit | **DONE** — see docs/assessments/hull-library-audit.md | — |
| Wave 2 | Parametric spec.yml generator | Not started | Bridge hull_library→DiffractionSpec |
| Wave 2 | RAO extraction and database | RAODatabase schema exists, no OrcaWave extractor | Need .owr parser |
| Wave 3 | OrcaFlex frame static (#1264) | 2D structural code exists (11 modules) | OrcaFlex model not built |
| Wave 3 | OrcaFlex parachute dynamic (#1292) | Not started | Depends on Wave 3 static |

### Priority Recommendations (aligned with plan)

1. **Immediate** — Harden solver queue (batch submit, result watcher). This unblocks everything.
2. **Short-term** — Build parametric spec.yml generator (bridge hull_library to DiffractionSpec). Small module (~200 lines), huge leverage.
3. **Short-term** — Seed hull registry with 5–10 standard hull forms (barge, tanker, semi-sub, spar, FPSO).
4. **Medium-term** — Automate OrcaWave→OrcaFlex handoff (RAO extraction → vessel type generation).
5. **Medium-term** — Complete parachute frame analysis chain (static #1264, then dynamic #1292).
6. **Longer-term** — Capytaine integration (#1440/#1464), DLC matrix generation, VIV module.

---

## Appendix: File Counts

```
OrcaWave skills:     8  (.claude/skills/engineering/marine-offshore/orcawave/)
OrcaFlex skills:    24  (.claude/skills/engineering/marine-offshore/orcaflex/)
Diffraction code:   55  (digitalmodel/src/digitalmodel/hydrodynamics/diffraction/)
OrcaWave reporting: 13  (digitalmodel/src/digitalmodel/orcawave/)
OrcaFlex solver:   259  (digitalmodel/src/digitalmodel/solvers/orcaflex/)
OrcaFlex reporting: 14  (digitalmodel/src/digitalmodel/orcaflex/)
Hull library:       25  (digitalmodel/src/digitalmodel/hydrodynamics/hull_library/)
Parametric hull:     8  (digitalmodel/src/digitalmodel/hydrodynamics/parametric_hull_analysis/)
Solver queue:        3  (scripts/solver/)
dat-to-yaml:         4  (scripts/data/orcaflex/)
Diffraction tests:  38  (digitalmodel/tests/hydrodynamics/diffraction/)
OrcaFlex tests:    101  (digitalmodel/tests/solvers/orcaflex/ + tests/orcaflex/)
Hull lib tests:     34  (digitalmodel/tests/hydrodynamics/hull_library/)
Spec.yml files:     13  (digitalmodel/docs/domains/orcawave/)
OrcaWave examples:   6  (L01-L06, digitalmodel/docs/domains/orcawave/examples/)
```
