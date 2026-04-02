# OrcaWave / OrcaFlex Domain Capability Roadmap

> **Date:** 2026-04-02  
> **Issue:** #1572 (Domain-specific capability roadmaps)  
> **Parent:** #1567 (Continuous Repo Architecture Intelligence)  
> **Cross-reference:** docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md  
> **Companion:** docs/assessments/hull-library-audit.md (hull library deep-dive)

---

## Executive Summary

The OrcaWave/OrcaFlex domain encompasses **344 Python modules**, **43 AI agent skills**, **~100 test files**, and **13 spec.yml validation cases**. The codebase is organized into four major code areas:

| Area | Modules | Purpose |
|------|---------|---------|
| `hydrodynamics/diffraction/` | 58 | Unified diffraction schema, multi-solver backend (AQWA + OrcaWave), benchmarking |
| `solvers/orcaflex/` | 259 | Full OrcaFlex lifecycle: generate → validate → run → post-process → report |
| `orcawave/` (reporting) | 13 | OrcaWave HTML reporting (8-section, Plotly) |
| `orcaflex/` (reporting+QA) | 14 | OrcaFlex HTML reporting (8-section) + QA facade |

Supporting infrastructure: `hull_library/` (25 modules, 7,656 LOC), `parametric_hull_analysis/` (7 modules, 1,983 LOC), solver queue (`scripts/solver/`, 4 files), dat-to-yaml pipeline (`scripts/data/orcaflex/`, 4 files).

**Key finding:** The software is architecturally mature but has critical gaps in **end-to-end integration testing** (no real BEM runs through the pipeline) and **solver queue automation** (batch submission, result watching, and post-processing hooks not yet built).

---

## 1. OrcaWave Capabilities

### 1.1 AI Agent Skills (8 skills)

| Skill | Summary | Linked Code Modules | Open Issues |
|-------|---------|--------------------| ------------|
| `orcawave` (root) | Index/navigator for all sub-skills | — | — |
| `orcawave/analysis` | Core diffraction/radiation: added mass, damping, QTF, batch, OrcaFlex export | `orcawave.orcawave_analysis`, `orcawave.batch`, `orcawave.orcaflex_export` | #22, #29 |
| `orcawave/aqwa-benchmark` | Cross-validation: OrcaWave vs AQWA (5% tolerance) | `diffraction.comparison_framework`, converters | #21, #29 |
| `orcawave/damping-sweep` | Viscous roll damping parametric: bilge keel, model test | `orcawave.damping` (DampingSweep, CriticalDampingCalculator) | — |
| `orcawave/mesh-generation` | CAD/STL → GDF, waterline refinement, convergence studies | `orcawave.mesh`, `orcawave.converters` | — |
| `orcawave/multi-body` | Side-by-side, FPSO-tanker, gap resonance, shielding | `orcawave.multibody` (MultiBodyAnalysis, GapResonanceAnalyzer) | — |
| `orcawave/qtf-analysis` | Full QTF matrix, Newman approx, slow-drift, mean drift | `orcawave.qtf` (FullQTFComputation, MeanDriftAnalyzer) | — |
| `orcawave/to-orcaflex` | .owr → OrcaFlex vessel types, RAO import, coord transforms | `diffraction.orcaflex_exporter`, `orcawave.rao_import` | — |

### 1.2 Supporting Skills

| Skill | Summary | Linked Code |
|-------|---------|-------------|
| `diffraction-analysis` | Master orchestrator: routes to AQWA/OrcaWave/BEMRosetta, defines DiffractionSpec | All diffraction modules |
| `hydrodynamic-analysis` | BEM theory: RAO, added mass, damping, wave loading | Reference only |
| `hydrodynamics` | Coefficient DB, wave spectra, OCIMF, RAO quality | `hydrodynamics.*` modules |
| `naval-architecture` | Hydrostatics, stability, seakeeping, hull types | Reference only |
| `solver-benchmark` | N-way cross-validation (AQWA/OrcaWave/BEMRosetta) | `MultiSolverComparator` |
| `mesh-utilities` | Quick mesh inspect/convert/validate | Mesh tools |

### 1.3 Code Modules

#### `digitalmodel/src/digitalmodel/orcawave/` — Reporting (13 files)

Builder-pattern HTML report generator with 8 sections:

| Section | Module | Content |
|---------|--------|---------|
| 1. Model Summary | `model_summary.py` | Body count, freq range, headings, water depth |
| 2. RAO Plots | `rao_plots.py` | Interactive Plotly RAO per DOF, tabbed UI |
| 3. Hydro Matrices | `hydro_matrices.py` | Added mass & damping diagonal line plots |
| 4. Mean Drift | `mean_drift.py` | Mean drift table + polar plot |
| 5. Panel Pressures | `panel_pressures.py` | Panel geometry stats (area, wetted surface) |
| 6. Multi-Body | `multi_body.py` | Coupling matrix heatmap |
| 7. QTF Heatmap | `qtf_heatmap.py` | QTF magnitude heatmap (ω₁ vs ω₂) |
| 8. QA Summary | `qa_summary.py` | Pass/fail checks (RAOs finite, damping ≥0) |

Entry point: `generate_orcawave_report(owr_path) → HTML`

#### `hydrodynamics/diffraction/` — Core Pipeline (58 files)

| Group | Files | Key Classes/Functions |
|-------|-------|----------------------|
| **Core Schema** | 4 | `DiffractionSpec`, `DiffractionResults`, `RAOSet`, `OutputValidator` |
| **OrcaWave Backend** | 5 | `OrcaWaveRunner`, `OrcaWaveBatchRunner`, `OrcaWaveConverter` |
| **AQWA Backend** | 7 | `AQWARunner`, `AQWABatchRunner`, `AQWAConverter`, `AQWALisParser` |
| **Benchmark** | 13 | `BenchmarkRunner`, `BenchmarkPlotter`, correlation, RAO helpers |
| **Multi-Solver** | 2 | `MultiSolverComparator`, `DiffractionComparator` |
| **Report** | 7 | `ReportGenerator`, header/response/hydrostatics builders |
| **Export** | 5 | `OrcaFlexExporter`, `PolarsExporter`, `RAOPlotter`, `SpecConverter` |
| **Mesh** | 3 | `GmshMeshBuilder`, mesh pipeline, geometry quality checker |
| **CLI** | 2 | CLI entry points for diffraction analysis |
| **Batch** | 3 | `BatchProcessor`, units, WAMIT reference loader |
| **Solver sub-pkg** | 3 | `OrcaWaveDataExtractor`, report extractors |

**DiffractionSpec Pipeline (the key scaling lever):**
```
spec.yml (20-30 lines, human-authored)
  → DiffractionSpec.from_yaml() (Pydantic v2 validation, 789 lines)
  → OrcaWaveBackend.generate() (unit conversion, mesh path resolution)
  → Native OrcaWave YAML (~180 lines)
  → solver queue → licensed-win-1
  → .owr result → OrcaWaveConverter → DiffractionResults
  → HTML report / OrcaFlex export / RAO database
```

### 1.4 Test Coverage

| Test Area | Files | Coverage |
|-----------|-------|----------|
| Diffraction (all solvers) | 32 | Schema, backend, benchmark, CLI, reports, RAO plotting |
| OrcaWave workflows | 3 | COM connection, end-to-end, integration |
| OrcaWave solver setup | 1 | Setup/fixture tests |
| Specialized CLI | 1 | diffraction_cli |

**Total: 37 test files for OrcaWave/diffraction domain**

### 1.5 Spec.yml Catalog (13 files)

| Level | Cases | Type | Purpose |
|-------|-------|------|---------|
| L00 (10 cases) | 2.1-2.3, 2.6-2.9, 3.1-3.3 | WAMIT validation | Primitive geometries for solver verification |
| L02 | Barge 80×40×10m | Benchmark | Standard diffraction |
| L03 | Ship ~220m | Benchmark | Full QTF + roll damping |
| L04 | Spar D=25m, T=110m | Benchmark | rad/s frequency input |

### 1.6 OrcaWave Examples (L01-L06)

| Example | Description | Key Content |
|---------|-------------|-------------|
| L01 | Default vessel | License test, API scripts, execution summary |
| L02 | OC4 Semi-sub | .yml, .gdf, .owr, workspace |
| L03 | Semi-sub multibody | Centre + outer column meshes (body + CS) |
| L04 | Sectional bodies | Column + keystone + pontoon, static/dynamic workspaces |
| L05 | Panel pressures | Same geometry, pressure output |
| L06 | Full QTF | Run script only |

---

## 2. OrcaFlex Capabilities

### 2.1 AI Agent Skills (25 skills)

| Skill | Summary | Linked Code |
|-------|---------|-------------|
| `orcaflex` (root) | Index: 24 sub-skills across 6 categories | — |
| **Modeling** | | |
| `model-generator` | Spec.yml → modular YAML via builder registry | `modular_generator/` |
| `modeling` | Universal runner: static/dynamic/batch | `universal/` |
| `line-wizard` | Line Setup Wizard tension/length calculation | `orcaflex_model_linesetup_wizard` |
| `vessel-setup` | 6-DOF vessel config, RAO import | `preprocess/load_vessel` |
| `monolithic-to-modular` | .dat → spec-driven modular with semantic validation | `modular_generator.extractor` |
| `model-sanitization` | Strip client data, legal scan, library ingest | `scripts/sanitize_s7_models.py` |
| `yaml-gotchas` | 10+ production-proven YAML trap fixes | `modular_generator/` |
| **Environment & Setup** | | |
| `environment-config` | JONSWAP, current, wind, seabed config | `environment_components` |
| `rao-import` | AQWA/OrcaFlex/CSV RAO import + validation | `marine_analysis.rao_processor` |
| **Analysis** | | |
| `batch-manager` | 100+ case batch with parallel + checkpointing | `batch_processor` |
| `installation-analysis` | Structure lowering, splash zone, crane ops | `orcaflex_installation` |
| `jumper-analysis` | Rigid/flexible: installation + in-place + VIV | `modular_generator` |
| `mooring-iteration` | scipy/Newton-Raphson tension optimization | `mooring_tension_iteration/` |
| `modal-analysis` | Natural frequencies, mode shapes, VIV screening | `orcaflex_modal_analysis` |
| `operability` | Weather downtime, scatter diagram analysis | `operability_analysis` |
| `extreme-analysis` | Max/min extraction with linked statistics | `opp_linkedstatistics` |
| `specialist` | Expert OrcFxAPI patterns, Monte Carlo | OrcFxAPI direct |
| **Post-Processing** | | |
| `post-processing` | OPP framework: stats, range graphs, HTML reports | `opp`, `orcaflex_utilities` |
| `visualization` | Model views, time series, polar, interactive HTML | `opp_visualization` |
| **Validation** | | |
| `code-check` | DNV/API/ISO capacity + safety factor checks | `structural_analysis.capacity` |
| `results-comparison` | Cross-sim comparison: tension, stiffness | `orcaflex.analysis.comparative` |
| `spec-audit` | Spec quality scoring (0-100), schema validation | `scripts/audit_spec_library.py` |
| `static-debug` | Static convergence troubleshooting | Reference only |
| **Utilities** | | |
| `file-conversion` | .dat ↔ .yml ↔ .sim bidirectional (98.9% success) | `orcaflex_yml_converter` |

### 2.2 Supporting Skills

| Skill | Summary | Linked Code |
|-------|---------|-------------|
| `mooring-analysis` | Station-keeping, catenary, anchor design (API/DNV/ISO) | Reference only |
| `mooring-design` | CALM/SALM buoy, spread mooring, material selection | Reference only |
| `catenary-riser` | Catenary + lazy wave riser: static shape, OrcaFlex export | `subsea.catenary.*` |
| `viv-analysis` | VIV screening, fatigue damage (DNV-RP-F105) | `subsea.viv_analysis.*` |

### 2.3 Code Modules

#### `digitalmodel/src/digitalmodel/orcaflex/` — Reporting + QA (14 files)

Mirror of OrcaWave reporting but for time-domain results:

| Section | Module | Content |
|---------|--------|---------|
| 1. Model Summary | `model_summary.py` | Object counts (lines/vessels/buoys), env params |
| 2. Static Config | `static_config.py` | Line profiles, vessel positions |
| 3. Time Series | `time_series.py` | Vessel DOFs, line tensions |
| 4. Range Graphs | `range_graphs.py` | Arclength vs min/max envelope |
| 5. Code Check | `code_check.py` | Utilization table (off by default) |
| 6. Mooring Loads | `mooring_loads.py` | Fairlead tensions (off by default) |
| 7. Modal Analysis | `modal_analysis.py` | Natural frequencies/periods (off by default) |
| 8. QA Summary | `qa_summary.py` | QA results from JSON files |

#### `digitalmodel/src/digitalmodel/solvers/orcaflex/` — Full Lifecycle (259 files)

| Subpackage | Files | Purpose |
|-----------|-------|---------|
| `core/` | 9 | Interfaces, base classes, component registry |
| `universal/` | 6 | Universal runner: any dir, any machine |
| `modular_generator/` | 30+ | Spec → modular YAML: builders, schema, routers |
| `format_converter/` | 10 | Three-way conversion: spec ↔ modular ↔ monolithic |
| `modular_input_validation/` | 10 | L1-L3 YAML validation + reporters |
| `reporting/` | 20+ | Extract → Model → Render reports |
| `mooring_analysis/` | 14 | Comprehensive mooring: stiffness, fenders, groups |
| `mooring_tension_iteration/` | 5 | Automated tension optimization |
| `analysis/` | 4 | Comparative analysis |
| `examples_integration/` | 14 | Download/convert official Orcina examples |
| Top-level | 40+ | OPP (8 files), converters, analysis, installation |
| `post_results/` | 8 | Legacy post-processing |

**Solver Queue Pipeline:**
```
scripts/solver/submit-job.sh  → queue/pending/{job_id}.yaml
scripts/solver/process-queue.py  (on licensed-win-1, polls every 30 min)
  → runs OrcFxAPI → queue/completed/{job_id}/
scripts/solver/setup-scheduler.ps1  (Windows Task Scheduler config)
```

**Dat-to-YAML Pipeline:**
```
scripts/data/orcaflex/dat-to-yaml.py  — convert .dat to .yml
scripts/data/orcaflex/enrich-and-clean.py  — add metadata, remove PII
```

### 2.4 Test Coverage

| Test Area | Files | Coverage |
|-----------|-------|----------|
| Solvers/OrcaFlex | 52 | format converter (7), modular generator (24), mooring analysis (5), reporting (12), examples (3), universal (1) |
| OrcaFlex (top-level) | 14 | CLI, converter, hybrid, library, load, optimization, pipeline, template |
| OrcaFlex reporting | 1 | orcaflex_reporting |
| Signal processing | 1 | tension analysis |
| Workflows (OrcaFlex) | 1 | template library |
| Agent tests | 1 | orcaflex_agent |

**Total: 70 test files for OrcaFlex domain**

---

## 3. Open GitHub Issues

### 3.1 Direct OrcaWave/OrcaFlex Issues

| Issue | Title | Priority | Labels |
|-------|-------|----------|--------|
| #1572 | Domain-specific capability roadmaps — OrcaWave/OrcaFlex, structural, hydrodynamics, pipeline | **high** | cat:engineering |
| #1464 | Capytaine BEM available for hull mesh wave load analysis | low | cat:engineering |
| #1440 | Install Capytaine BEM solver into ACE ecosystem | — | dev-secondary |
| #1319 | Hull form parametric design — coefficients and Series 60 | — | wrk-item |
| #1314 | Ship-specific hydrostatic data tables (DDG-51, FFG-7) | — | wrk-item |
| #1292 | OrcaFlex parachute deployment template — time-domain snap load analysis | low | cat:engineering |
| #1268 | CFD analysis plan — car + parachute aerodynamics, time-marching deployment | **high** | cat:engineering |
| #1264 | OrcaFlex frame analysis | **high** | cat:engineering |
| #1242 | Parachute frame force calculation — drag car parachute deployment | medium | structural-dynamics |
| #569 | Vandiver (1987) hydrodynamic damping model implementation | **high** | archived |
| #29 | Run 3-way benchmark on Unit Box hull | — | — |
| #28 | OFFPIPE Integration — pipelay cross-validation against OrcaFlex | — | — |
| #24 | OrcaFlex drilling and completion riser parametric analysis | — | — |
| #23 | OrcaFlex rigid jumper analysis — stress and VIV | — | — |
| #22 | Parametric hull form analysis with RAO generation | — | — |
| #21 | SPM project benchmarking — AQWA vs OrcaFlex | — | — |
| #20 | OrcaFlex structure deployment analysis — supply boat side deployment | — | — |
| #19 | Modular OrcaFlex pipeline installation input with parametric campaign | — | — |

### 3.2 Related Infrastructure Issues

| Issue | Title | Relationship |
|-------|-------|-------------|
| #1567 | Continuous Repo Architecture Intelligence | Parent of #1572 |
| #1442 | Integrate FEniCSx PDE solver | Alternative BEM/FEM solver |
| #1363 | LLM domain-tag riser-eng-job literature | Riser knowledge base |
| #1360 | Extract algorithms from riser-eng-job archives | Riser methods |

---

## 4. Gap Analysis

### 4.1 What's NOT Yet Automated

| Workflow | Current State | Gap | Impact |
|----------|--------------|-----|--------|
| **Parametric spec.yml generation** | Manual spec.yml authoring | No `parametric_spec_generator.py` | Blocks automated hull form sweeps (#22) |
| **Solver queue batch submission** | Single-job `submit-job.sh` | No `submit-batch.sh` or YAML manifest | Can't submit parametric sweeps |
| **Result watching + auto post-processing** | Manual check of `queue/completed/` | No `watch-results.sh` or `post-process-hook.py` | Manual intervention after every run |
| **End-to-end BEM pipeline test** | Each component tested in isolation | No test runs DiffractionSpec → solver → results → report | Pipeline integration risk |
| **Capytaine production integration** | Installed on dev-secondary | `sweep.py` imports but no end-to-end test | Open-source BEM not usable yet (#1464) |
| **Series 60 hull forms** | Parametric space handles L/B/T/Cb | No Todd-Wigley form coefficients | Limited hull variety (#1319) |
| **OrcaFlex frame analysis** | 2D frame solver exists in parachute/ | No OrcaFlex model builder for frames | Blocks #1264, #1292 |
| **Cross-tool comparison** | Manual | No `CrossToolComparison` class | Can't validate 2D vs OrcaFlex vs CalculiX |
| **RAO extraction from .owr** | OrcaWave reporting reads .owr | No standalone `RAOExtractor` for database population | RAO database can't be populated from runs |
| **Automated benchmark runs** | Benchmark framework ready | No submitted jobs for Unit Box (#29) | 3-way benchmark stalled |

### 4.2 What's Missing for Production Use

| Category | Missing | Priority |
|----------|---------|----------|
| **Hull Library** | Centralized hull parameter registry (`hull_registry.yaml`) | Medium |
| **Hull Library** | Series 60 parent forms (#1319) | Medium |
| **Hull Library** | Ship-specific hydrostatics DDG-51/FFG-7 (#1314) | Low |
| **Parametric Analysis** | Tests for forward_speed, shallow_water, passing_ship_sweep, charts | Medium |
| **Solver Queue** | Batch submission, result watcher, auto post-processing | **High** |
| **Solver Queue** | Job status dashboard / health monitoring | Medium |
| **OrcaWave Pipeline** | Parametric spec.yml generator | **High** |
| **OrcaWave Pipeline** | RAO extractor → database pipeline | **High** |
| **OrcaFlex** | Frame analysis model builder (#1264) | **High** |
| **OrcaFlex** | Dynamic deployment model (#1292) | Medium |
| **OrcaFlex** | Cross-tool comparison framework | Medium |
| **Testing** | End-to-end pipeline integration test | **High** |
| **Testing** | Parametric hull analysis dedicated test suite | Medium |

### 4.3 Skill → Code → Test Matrix (Key Gaps)

| Skill | Has Code Module | Has Tests | Gap |
|-------|----------------|-----------|-----|
| orcawave/analysis | ✅ | ✅ (3 workflow tests) | End-to-end with real solver |
| orcawave/aqwa-benchmark | ✅ | ✅ (benchmark tests) | No submitted benchmark jobs |
| orcawave/damping-sweep | ✅ | ❌ | No test file found |
| orcawave/mesh-generation | ✅ | ✅ (mesh tests) | — |
| orcawave/multi-body | ✅ | ✅ (L03 spec) | — |
| orcawave/qtf-analysis | ✅ | ✅ (L03 spec has QTF) | — |
| orcawave/to-orcaflex | ✅ | ❌ | No integration test for .owr → OrcaFlex |
| orcaflex/model-generator | ✅ | ✅ (24 tests) | Well covered |
| orcaflex/mooring-iteration | ✅ | ✅ (5 tests) | — |
| orcaflex/batch-manager | ✅ | ✅ (via universal) | — |
| orcaflex/installation-analysis | ✅ | ❌ | No dedicated test |
| orcaflex/jumper-analysis | ✅ | ❌ | No dedicated test |

---

## 5. Cross-Reference with Intensive Plan

The [2026-04-01 Intensive Plan](../plans/2026-04-01-orcawave-orcaflex-intensive-plan.md) defines 3 waves. Status against this roadmap:

### Wave 1: Solver Queue Hardening

| Task | Plan Status | Roadmap Finding |
|------|-------------|-----------------|
| 1.1 Licensed-win-1 assignment | Documented | 1 completed run, 1 failed run on record |
| 1.2 Batch job submission | Planned | `submit-job.sh` exists, `submit-batch.sh` NOT built |
| 1.3 Result watcher | Planned | NOT built |
| 1.4 Submit benchmark jobs (#29) | Planned | NOT submitted |

### Wave 2: DiffractionSpec Pipeline Scaling

| Task | Plan Status | Roadmap Finding |
|------|-------------|-----------------|
| 2.1 Audit hull library | **DONE** | See docs/assessments/hull-library-audit.md — 100% implemented |
| 2.2 Parametric spec.yml generator | Planned | NOT built — hull_library has all prerequisites |
| 2.3 RAO extraction + database + reports | Planned | RAODatabase exists (Parquet), extractor NOT built |
| 2.4 Submit parametric batch | Planned | NOT submitted |

### Wave 3: OrcaFlex Frame Analysis

| Task | Plan Status | Roadmap Finding |
|------|-------------|-----------------|
| 3.1 Frame geometry extraction | Planned | 2D exists in parachute/, 3D geometry exists |
| 3.2 Static frame model builder (#1264) | Planned | NOT built |
| 3.3 Dynamic deployment model (#1292) | Planned | NOT built |
| 3.4 Cross-tool comparison | Planned | NOT built |
| 3.5 Submit frame jobs | Planned | NOT submitted |

**Summary:** Wave 2 Task 2.1 (audit) is complete. Everything else in the plan is still pending implementation.

---

## 6. Recommended Priorities

### Immediate (Enables everything else)

1. **Build `submit-batch.sh` + `batch-manifest.yaml`** — Unblocks all solver queue work
2. **Build `watch-results.sh` + `post-process-hook.py`** — Automates result collection
3. **Build `parametric_spec_generator.py`** — Generates spec.yml from sweep definitions

### Short-Term (Validates the pipeline)

4. **Submit Unit Box benchmark jobs (#29)** — Validates solver queue end-to-end
5. **Build OrcaFlex frame model builder (#1264)** — Unblocks parachute analysis
6. **Write integration test: DiffractionSpec → backend → mock solver → results**

### Medium-Term (Scales the capability)

7. **Build RAO extractor → database pipeline** — Populates RAODatabase from real runs
8. **Add Series 60 hull forms (#1319)** — Expands parametric hull variety
9. **Run small parametric sweep through full pipeline** — Proves the architecture
10. **Build cross-tool comparison framework (#1242)** — 2D vs OrcaFlex vs CalculiX

---

## Appendix A: Complete Skills Inventory

### OrcaWave Skills (8)

```
.claude/skills/engineering/marine-offshore/orcawave/
  SKILL.md                  -- Root index
  analysis/SKILL.md         -- Core diffraction/radiation analysis
  aqwa-benchmark/SKILL.md   -- OrcaWave vs AQWA cross-validation
  damping-sweep/SKILL.md    -- Viscous roll damping parametric
  mesh-generation/SKILL.md  -- CAD/STL → GDF mesh generation
  multi-body/SKILL.md       -- STS, FPSO-tanker, gap resonance
  qtf-analysis/SKILL.md     -- Full QTF, Newman approx, slow-drift
  to-orcaflex/SKILL.md      -- .owr → OrcaFlex vessel type export
```

### OrcaFlex Skills (25)

```
.claude/skills/engineering/marine-offshore/orcaflex/
  SKILL.md                      -- Root index (24 sub-skills)
  batch-manager/SKILL.md        -- 100+ case parallel batch
  code-check/SKILL.md           -- DNV/API/ISO capacity checks
  environment-config/SKILL.md   -- JONSWAP, current, wind, seabed
  extreme-analysis/SKILL.md     -- Max/min with linked stats
  file-conversion/SKILL.md      -- .dat ↔ .yml ↔ .sim (98.9%)
  installation-analysis/SKILL.md -- Structure lowering, splash zone
  jumper-analysis/SKILL.md      -- Rigid/flexible jumper lifecycle
  line-wizard/SKILL.md          -- Line Setup Wizard
  modal-analysis/SKILL.md       -- Natural freq, mode shapes, VIV
  model-generator/SKILL.md      -- Spec → modular YAML (V2.0)
  modeling/SKILL.md             -- Universal runner
  model-sanitization/SKILL.md   -- Client data scrubbing
  monolithic-to-modular/SKILL.md -- Extraction + semantic validation
  mooring-iteration/SKILL.md    -- scipy/Newton tension optimization
  operability/SKILL.md          -- Weather downtime analysis
  post-processing/SKILL.md      -- OPP framework
  rao-import/SKILL.md           -- AQWA/OrcaFlex/CSV RAO import
  results-comparison/SKILL.md   -- Cross-sim comparison
  spec-audit/SKILL.md           -- Quality scoring (0-100)
  specialist/SKILL.md           -- Expert OrcFxAPI patterns
  static-debug/SKILL.md         -- Convergence troubleshooting
  vessel-setup/SKILL.md         -- 6-DOF vessel configuration
  visualization/SKILL.md        -- Model views, plots, HTML
  yaml-gotchas/SKILL.md         -- Production YAML trap catalog
```

### Marine-Offshore Supporting Skills (10)

```
.claude/skills/engineering/marine-offshore/
  diffraction-analysis/SKILL.md    -- Master diffraction orchestrator
  hydrodynamic-analysis/SKILL.md   -- BEM theory reference
  hydrodynamics/SKILL.md           -- Coefficient DB, wave spectra
  naval-architecture/SKILL.md      -- Hydrostatics, stability, seakeeping
  solver-benchmark/SKILL.md        -- N-way cross-validation
  mesh-utilities/SKILL.md          -- Quick mesh inspect/convert
  mooring-analysis/SKILL.md        -- Mooring design reference
  mooring-design/SKILL.md          -- CALM/SALM/spread design
  catenary-riser/SKILL.md          -- Catenary + lazy wave riser
  viv-analysis/SKILL.md            -- VIV screening + fatigue
```

## Appendix B: Module Counts

| Directory | Python Files | Test Files | LOC (est.) |
|-----------|-------------|------------|------------|
| `orcawave/` | 13 | 3 | ~1,500 |
| `orcaflex/` | 14 | 1 | ~1,800 |
| `hydrodynamics/diffraction/` | 58 | 37 | ~15,000 |
| `hydrodynamics/hull_library/` | 25 | 27 | ~7,656 |
| `hydrodynamics/parametric_hull_analysis/` | 7 | 1 | ~1,983 |
| `solvers/orcaflex/` | 259 | 70 | ~50,000+ |
| `scripts/solver/` | 2 (+2 shell) | 0 | ~500 |
| `scripts/data/orcaflex/` | 2 (+1 archived) | 0 | ~300 |
| **Total** | **380** | **139** | **~79,000** |
