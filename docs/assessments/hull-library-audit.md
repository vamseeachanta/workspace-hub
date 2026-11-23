# Hull Library and Parametric Analysis Infrastructure Audit

> **Date:** 2026-04-02  
> **Parent issue:** #1567 (Continuous Repo Architecture Intelligence)  
> **Plan reference:** docs/plans/2026-04-01-orcawave-orcaflex-intensive-plan.md — Wave 2 Task 2.1  
> **Scope:** Full audit of hull form generation, parametric analysis, mesh handling, and RAO database infrastructure

---

## Executive Summary

The hull library and parametric analysis infrastructure is **substantially more mature than expected**. Across two packages — `hull_library/` (25 modules, ~7,656 lines) and `parametric_hull_analysis/` (7 modules, ~1,983 lines) — **every module is fully implemented** with zero stubs, zero `pass`-only methods, and zero `NotImplementedError` raises. The test suite is comprehensive (25 hull_library test files, plus diffraction tests).

**Recommendation:** Extend the existing infrastructure. Do NOT build new. The existing `hull_library` already has the mesh generation, parametric scaling, RAO database, and catalog system needed for the parametric hull sweeps described in Wave 2 of the intensive plan.

---

## 1. Hull Library Package

**Location:** `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/`  
**Modules:** 25 Python files (excluding `__pycache__`)  
**Total lines:** ~7,656  
**Implementation status:** 100% REAL (0 stubs)

### 1.1 Architecture Layers

| Layer | Modules | Purpose | Lines |
|-------|---------|---------|-------|
| **Schema/Data** | `profile_schema.py`, `panel_catalog.py`, `rao_database.py` | Pydantic v2 models, validation, persistence | ~839 |
| **Mesh Generation** | `mesh_generator.py` | Full quad panelization with adaptive density | ~504 |
| **Line Generator** | `line_generator/` (4 submodules) | Line definition → surface → panels → export | ~1,279 |
| **Mesh Manipulation** | `mesh_scaler.py`, `mesh_refiner.py`, `coarsen_mesh.py`, `decimation.py`, `decimation_vtk.py`, `decimation_gmsh.py`, `_decimation_helpers.py` | Scale, refine, coarsen, decimate (3 backends: QEM, VTK, GMSH) | ~1,623 |
| **Lookup/Query** | `catalog.py`, `lookup.py`, `parametric_hull.py`, `analysis_setup.py` | Hull catalog, nearest-neighbor, parametric space, analysis config | ~1,355 |
| **RAO System** | `rao_registry.py`, `rao_database.py`, `rao_lookup_plots.py` | Registry, Parquet-backed DB, Plotly visualization | ~840 |
| **Visualization** | `schematic_generator.py` | Pure-stdlib SVG — profile, plan, body views | ~519 |

### 1.2 Module-by-Module Audit

#### Schema / Data

| Module | Lines | Classes | Key API | Tests |
|--------|-------|---------|---------|-------|
| `profile_schema.py` | 333 | `HullProfile`, `StationData`, `HullVariation`, `MeshGeneratorConfig` | Pydantic v2 validation, `HullProfile.from_yaml()` | `test_profile_schema.py` |
| `panel_catalog.py` | 214 | `PanelCatalog`, `PanelEntry` | Register/query panels, export to GDF/DAT | `test_panel_catalog.py` |
| `panel_inventory.py` | 152 | `PanelInventory` | Track panel meshes by hull + config | `test_panel_inventory.py` |

#### Mesh Generation

| Module | Lines | Classes | Key API | Tests |
|--------|-------|---------|---------|-------|
| `mesh_generator.py` | 504 | `HullMeshGenerator`, `PanelMesh` | `generate(profile, config)` → quad panels with adaptive density, waterline refinement | `test_mesh_generator.py` |
| `mesh_scaler.py` | 204 | `MeshScaler` | Uniform and non-uniform (L/B/T independent) scaling | `test_mesh_scaler.py` |
| `mesh_refiner.py` | 228 | `MeshRefiner` | Panel subdivision, waterline grading | `test_mesh_refiner.py` |
| `coarsen_mesh.py` | 187 | `MeshCoarsener` | Reduce panel count while preserving geometry | `test_coarsen_mesh.py` |

#### Decimation (3 backends)

| Module | Lines | Key API | Tests |
|--------|-------|---------|-------|
| `decimation.py` | 342 | Pure NumPy QEM (Quadric Error Metrics) | `test_decimation.py` |
| `decimation_vtk.py` | 285 | VTK-backed decimation (lazy import) | `test_decimation_vtk.py` |
| `decimation_gmsh.py` | 267 | GMSH-backed decimation (lazy import) | `test_decimation_gmsh.py` |
| `_decimation_helpers.py` | 155 | Shared utilities (edge collapse, topology) | — |

#### Line Generator Sub-Package

| Module | Lines | Key API | Tests |
|--------|-------|---------|-------|
| `line_parser.py` | ~320 | Parse hull line definitions (stations, offsets) | `test_line_parser.py` |
| `hull_surface.py` | ~350 | B-spline surface interpolation from stations | `test_hull_surface.py` |
| `panelizer.py` | ~380 | Convert surface to quad panels with grading | `test_panelizer.py` |
| `exporter.py` | ~230 | Export to GDF (WAMIT), DAT (AQWA), STL | `test_exporter.py` |

#### Lookup and Catalog

| Module | Lines | Classes | Key API | Tests |
|--------|-------|---------|---------|-------|
| `catalog.py` | 412 | `HullCatalog`, `CatalogEntry` | YAML-backed hull registry, spectral analysis, search by parameters | `test_catalog.py`, `test_catalog_additional.py` |
| `lookup.py` | 375 | `HullLookup` | Nearest-neighbor matching by L/B/T/Cb, weighted distance | `test_lookup.py` |
| `parametric_hull.py` | 254 | `HullParametricSpace` | Cartesian product sweeps over L/B/T/Cb ranges | `test_parametric_hull.py` |
| `analysis_setup.py` | 183 | `AnalysisSetup` | Configure BEM analysis (frequencies, headings, solver) | `test_analysis_setup.py` |

#### RAO System

| Module | Lines | Classes | Key API | Tests |
|--------|-------|---------|---------|-------|
| `rao_database.py` | 292 | `RAODatabase`, `RAODatabaseEntry` | Parquet-backed storage, query by hull params, comparison | `test_rao_database.py` |
| `rao_registry.py` | 187 | `RAORegistry` | Track which hulls have computed RAOs | `test_rao_registry.py` |
| `rao_lookup_plots.py` | 361 | — (functions) | Plotly: RAO comparison, sensitivity, heatmaps | `test_rao_lookup_plots.py` |

#### Visualization

| Module | Lines | Key API | Tests |
|--------|-------|---------|-------|
| `schematic_generator.py` | 519 | Pure-stdlib SVG: profile view, plan view, body plan (3 naval architecture views) | `test_schematic_generator.py` |

### 1.3 External Dependencies

- **Required:** numpy, scipy, pydantic (v2), PyYAML
- **Optional (lazy-loaded):** plotly (RAO plots), pyvista (mesh viz), gmsh (decimation), pandas (dataframes)

### 1.4 Test Coverage

- **25 test files** in `digitalmodel/tests/hydrodynamics/hull_library/`
- **4 line_generator test files** in `line_generator/` subdirectory
- **2 additional test files** in `digitalmodel/tests/unit/hull_library/`
- **Conftest fixtures** for both hull_library and line_generator
- **Integration test:** `test_integration.py`, `test_panel_integration.py`
- Covers: all modules, including seed data, expansion, and extended catalog tests

---

## 2. Parametric Hull Analysis Package

**Location:** `digitalmodel/src/digitalmodel/hydrodynamics/parametric_hull_analysis/`  
**Modules:** 7 Python + 1 YAML manifest  
**Total lines:** ~1,983  
**Implementation status:** 100% REAL (0 stubs)

### 2.1 Module Audit

| Module | Lines | Key Content | Purpose |
|--------|-------|-------------|---------|
| `models.py` | 187 | `SweepConfig`, `PassingShipSweepConfig`, `SweepResultEntry`, `PassingShipSweepEntry`, `BankEffectResult`, `classify_depth()` | Pydantic v2 config + dataclass results |
| `sweep.py` | 316 | `run_parametric_sweep()`, `sweep_to_dataframe()` | Core orchestration: hull variants → BEM → RAOs → database |
| `forward_speed.py` | 346 | `wave_number()`, `encounter_frequency()`, `correct_rao_for_speed()`, `strip_theory_speed_correction()` | DNV-RP-C205 §7.4 forward speed corrections |
| `shallow_water.py` | 325 | `dnv_shallow_water_factor()`, `validate_shallow_water_results()`, `pianc_bank_suction_force()`, `pianc_bank_clearance_width()` | DNV-RP-C205 Table 7-1 + PIANC 121 bank effects |
| `passing_ship_sweep.py` | 284 | `run_passing_ship_sweep()`, `passing_ship_to_dataframe()`, `pianc_operability_check()` | Wang 1975 slender-body passing ship forces |
| `charts.py` | 441 | `rao_comparison_grid()`, `parameter_sensitivity_plot()`, `depth_sensitivity_plot()`, `passing_ship_contour()`, `operability_chart()` | Matplotlib batch visualization |
| `manifest.yaml` | 46 | CI/website traceability | Maps functions → DNV clauses |

### 2.2 Architecture

The parametric analysis package is an **orchestration layer** that ties together:
- `hull_library` — mesh generation and parametric space definition
- `capytaine` — BEM solver (open-source, Python-native)
- `passing_ship` — Wang 1975 slender-body forces

Pipeline: `SweepConfig` → `HullParametricSpace` (from hull_library) → generate meshes → export GDF → run BEM (Capytaine) → compute RAOs → store in `RAODatabase` → visualization via `charts.py`

### 2.3 Standards Compliance

- DNV-RP-C205 (2021): encounter frequency (§7.4), shallow water (Table 7-1), forward speed corrections
- PIANC 121: bank suction forces, clearance widths
- Wang 1975: slender-body passing ship interaction

### 2.4 Test Coverage

- `test_parametric_hull.py` covers the parametric hull space generation
- Sweep, forward speed, and shallow water tests exist via integration with hull_library tests
- **Gap:** No dedicated test files for `forward_speed.py`, `shallow_water.py`, `passing_ship_sweep.py`, `charts.py`

---

## 3. Existing Hull Data

### 3.1 Spec.yml Files (13 total)

#### Benchmark Specs (3 files — real engineering vessels)

| Spec | Vessel Name | Type | L (m) | B (m) | T (m) | Mass (te) | Water Depth | Mesh Format |
|------|-------------|------|--------|--------|--------|-----------|-------------|-------------|
| `L02_barge_benchmark/spec.yml` | Barge_Benchmark | Barge | ~80 | ~40 | ~10 | 16,400 | 200 m | GDF |
| `L03_ship_benchmark/spec.yml` | Body1 | Ship | ~220 | — | — | 9,018 | 500 m | DAT |
| `L04_spar_benchmark/spec.yml` | Spar_Benchmark | Spar | D=25 | — | T=110 | 55,000 | 200 m | DAT |

Note: L03 has full QTF + external roll damping. L04 uses rad/s frequency input.

#### WAMIT Validation Specs (10 files — primitive geometries)

| Case | Body | Type | Key Feature |
|------|------|------|-------------|
| 2.1 | Cylinder R=1m T=0.5m | Single body | Standard validation |
| 2.2 | Cylinder R=1m T=0.5m | Single body | Extended frequency range (0.1-10 rad/s, 100 values) |
| 2.3 | Cylinder R=1m T=0.5m | Single body | Trimmed body (15° trim, z=0.27m) |
| 2.6 | Cylinder + Spheroid | Multi-body | Shallow water (3m depth) |
| 2.7 | Pyramid (ZC=0.8) | Custom | Control surface, infinite depth |
| 2.8 | Ellipsoid (96 panels) | Custom | Bi-symmetric, control surface |
| 2.9 | Moonpool cylinder | Moonpool | Damping lid (factor 0.016) |
| 3.1 | Bottom-mounted cylinder | Fixed, full QTF | Free surface zone, h=1m |
| 3.2 | Sphere R=5 | Custom with lid | Bi-symmetric, h=3m |
| 3.3 | Cylinder + Ellipsoid | Multi-body | Fixed+free combination |

### 3.2 Hull Forms Data

**Location:** `digitalmodel/docs/domains/orcawave/hull_forms/`

| File | Description |
|------|-------------|
| `NeptuneBatchTestCase.yml` | **Skandi Neptune** OrcaFlex vessel model (35,110 lines, 1.27 MB). L=96.6m, mass=9,196 te, draught 5.551m (LC8). Full RAO data for multiple headings (0°-360° in 15° steps), periods 1-30s. |

### 3.3 Hull Library Documentation

**Location:** `digitalmodel/docs/domains/hull_library/`

| File | Content |
|------|---------|
| `hull_scaling_guide.md` | Explains uniform vs parametric (non-uniform L/B/T) scaling, re-panelization guidelines, code examples using `HullCatalog`, `HullVariation`, `MeshGeneratorConfig`, `HullMeshGenerator` |

### 3.4 OrcaWave Examples

**Location:** `digitalmodel/docs/domains/orcawave/examples/` (50 files, 8 subdirectories)

| Example | Description | Key Files |
|---------|-------------|-----------|
| `L01_default_vessel/` | License test, API execution | 15 files: .yml, .gdf, .owr, 5 Python scripts, results docs |
| `L02 OC4 Semi-sub/` | OC4 semi-submersible | .yml, .gdf, .owr, workspace |
| `L03 Semi-sub multibody/` | Multi-body semi-sub (centre + outer columns) | .yml, 4 .gdf meshes (body + CS) |
| `L04 Sectional bodies/` | Column + keystone + pontoon | .yml, 3 .gdf, dynamic + static workspaces |
| `L05 Panel pressures/` | Same geometry, panel pressure output | .yml, 3 .gdf |
| `L06 Full QTF/` | Full QTF analysis | run_orcawave.py only |
| `qa/` | QA results for L01-L06 | 6 JSON results, QA script + report |
| Root docs | `PARAMETER_REFERENCE.md`, `ORCAFLEX_MODELS.md`, `report_config_template.yml` |

---

## 4. Related GitHub Issues

### 4.1 Issue #1314: Ship-Specific Hydrostatic Data Tables (DDG-51, FFG-7)

- **Title:** WRK-1372: Ship-specific hydrostatic data tables (DDG-51, FFG-7)
- **State:** OPEN
- **Labels:** wrk-item, machine:dev-primary
- **Body:** Auto-created by backfill-github-refs.sh (minimal description)
- **Status:** No implementation found. The hull_library `catalog.py` has a general hull catalog, but no ship-specific hydrostatic tables (Bonjean curves, floodable length, stability) for DDG-51 or FFG-7 class vessels.
- **Relationship:** Would extend `hull_library` with naval vessel-specific data.

### 4.2 Issue #1319: Hull Form Parametric Design — Coefficients and Series 60

- **Title:** WRK-1377: Hull form parametric design — coefficients and Series 60
- **State:** OPEN
- **Labels:** wrk-item, machine:dev-primary
- **Body:** Auto-created by backfill-github-refs.sh (minimal description)
- **Status:** The parametric hull infrastructure exists (`parametric_hull.py`, `sweep.py`) but the **Series 60 systematic hull form series** is not yet implemented. The current parametric space uses generic L/B/T/Cb ranges but doesn't include the Todd-Wigley Series 60 parent form coefficients or regression equations.
- **Relationship:** Extend `HullParametricSpace` with Series 60 parent forms. The mesh generation pipeline is ready — it just needs the form coefficient data.

### 4.3 Other Related Issues

| Issue | Title | Priority | Status |
|-------|-------|----------|--------|
| #22 | Parametric hull form analysis with RAO generation and client-facing lookup | medium | The entire hull_library + parametric_hull_analysis package IS the implementation. Core pipeline exists but needs end-to-end integration testing with real BEM runs. |
| #29 | Run 3-way benchmark on Unit Box hull | medium | Benchmark infrastructure ready. Needs actual solver runs on licensed-win-1. |
| #1464 | Capytaine BEM available for hull mesh wave load analysis | low | Capytaine installed on dev-secondary but not yet integrated with sweep.py in production. |
| #1440 | Install Capytaine BEM solver into ACE ecosystem | — | Installation issue for dev-secondary. |

---

## 5. Assessment: Implemented vs Skeleton vs Gap

### 5.1 Fully Implemented (Production-Ready with Tests)

| Capability | Modules | Test Coverage |
|-----------|---------|---------------|
| Hull profile schema and validation | `profile_schema.py` | ✅ `test_profile_schema.py` |
| Hull catalog (YAML-backed registry) | `catalog.py` | ✅ `test_catalog.py`, `test_catalog_additional.py` |
| Nearest-neighbor hull lookup | `lookup.py` | ✅ `test_lookup.py` |
| Parametric space (L/B/T/Cb sweeps) | `parametric_hull.py` | ✅ `test_parametric_hull.py` |
| Mesh generation (quad panels, adaptive) | `mesh_generator.py` | ✅ `test_mesh_generator.py` |
| Mesh scaling (uniform + non-uniform) | `mesh_scaler.py` | ✅ `test_mesh_scaler.py` |
| Mesh refinement | `mesh_refiner.py` | ✅ `test_mesh_refiner.py` |
| Mesh coarsening | `coarsen_mesh.py` | ✅ `test_coarsen_mesh.py` |
| Mesh decimation (3 backends) | `decimation*.py` | ✅ 3 test files |
| Line generator pipeline | `line_generator/` | ✅ 4 test files |
| Panel catalog and inventory | `panel_catalog.py`, `panel_inventory.py` | ✅ 2 test files + integration |
| RAO database (Parquet) | `rao_database.py` | ✅ `test_rao_database.py` |
| RAO registry | `rao_registry.py` | ✅ `test_rao_registry.py` |
| SVG schematic generation | `schematic_generator.py` | ✅ `test_schematic_generator.py` |
| Parametric sweep orchestration | `sweep.py` | Partial (via integration) |
| Forward speed corrections (DNV) | `forward_speed.py` | **Gap** |
| Shallow water corrections (DNV/PIANC) | `shallow_water.py` | **Gap** |
| Passing ship sweeps | `passing_ship_sweep.py` | **Gap** |
| Visualization (matplotlib) | `charts.py` | **Gap** |

### 5.2 Identified Gaps

| Gap | Description | Severity | Recommended Action |
|-----|-------------|----------|-------------------|
| **No centralized hull parameter database** | L/B/T/Cb tracking across runs — the plan identified this. The `RAODatabase` stores results but doesn't centralize what parameters have been run. | Medium | Add `hull_registry.yaml` to `data/parametric_hulls/` as proposed in plan Task 2.2. Extend `HullCatalog` to read it. |
| **Series 60 hull form data** (#1319) | No Todd-Wigley Series 60 form coefficients. Parametric hull only does generic L/B/T/Cb. | Medium | Add Series 60 regression data to `profile_schema.py` or a new `series60.py`. The mesh generation pipeline is ready. |
| **Ship hydrostatic tables** (#1314) | No Bonjean curves, floodable length, or GZ curves for specific vessels. | Low | Out of scope for parametric RAOs. Track separately. |
| **Missing tests for parametric_hull_analysis** | `forward_speed.py`, `shallow_water.py`, `passing_ship_sweep.py`, `charts.py` have no dedicated tests. | Medium | Write tests — the functions are implemented but untested. |
| **Capytaine integration not production-tested** | `sweep.py` imports from capytaine, but no end-to-end test exists with actual BEM runs. | High | Run a small parametric sweep (3 hulls) through the full pipeline on dev-secondary where Capytaine is installed. |
| **No parametric spec.yml generator** | The DiffractionSpec pipeline validates spec.yml files, but there's no script to auto-generate them from a parametric sweep definition. | Medium | Build `parametric_spec_generator.py` as described in plan Task 2.2. |
| **Only 1 real hull form on file** | NeptuneBatchTestCase.yml is the only real vessel. Benchmark specs use simplified geometries. | Medium | Add more hull forms to catalog — start with Series 60 parent forms. |

### 5.3 Recommendation: Extend, Don't Rebuild

**EXTEND the existing hull_library.** The infrastructure is comprehensive and well-tested:

1. **For parametric spec.yml generation:** Use `HullParametricSpace` to generate hull variants → `HullMeshGenerator` to produce meshes → new `parametric_spec_generator.py` to write DiffractionSpec-compliant spec.yml files. The DiffractionSpec validation pipeline (`input_schemas.py`) already exists.

2. **For RAO storage:** Use the existing `RAODatabase` (Parquet-backed) and `RAORegistry`. Add a `hull_registry.yaml` for centralized parameter tracking.

3. **For visualization:** The hull_library already has Plotly RAO plots (`rao_lookup_plots.py`), SVG schematics (`schematic_generator.py`), and matplotlib charts (`charts.py`). Build the HTML report as a composition of these.

4. **For mesh operations:** The mesh generation, scaling, refinement, and decimation pipeline covers all needs. Three decimation backends provide flexibility.

5. **Next concrete step:** Write `parametric_spec_generator.py` (plan Task 2.2) that takes a sweep definition YAML and produces N spec.yml files validated by `DiffractionSpec.from_yaml()`. The hull_library provides the hull parametric space, mesh generation, and catalog infrastructure — all ready to go.

---

## Appendix: File Inventory

### hull_library/ (25 files, ~7,656 lines)

```
__init__.py                    # Package exports
profile_schema.py        (333) # HullProfile, StationData, HullVariation, MeshGeneratorConfig
catalog.py               (412) # HullCatalog, CatalogEntry — YAML-backed registry
lookup.py                (375) # HullLookup — nearest-neighbor by L/B/T/Cb
parametric_hull.py       (254) # HullParametricSpace — cartesian product sweeps
analysis_setup.py        (183) # AnalysisSetup — BEM config
mesh_generator.py        (504) # HullMeshGenerator, PanelMesh — quad panels
mesh_scaler.py           (204) # MeshScaler — uniform + non-uniform
mesh_refiner.py          (228) # MeshRefiner — subdivision, waterline grading
coarsen_mesh.py          (187) # MeshCoarsener
decimation.py            (342) # Pure NumPy QEM decimation
decimation_vtk.py        (285) # VTK-backed decimation
decimation_gmsh.py       (267) # GMSH-backed decimation
_decimation_helpers.py   (155) # Shared decimation utilities
panel_catalog.py         (214) # PanelCatalog — register/query panels
panel_inventory.py       (152) # PanelInventory — track panels by hull
rao_database.py          (292) # RAODatabase — Parquet storage, query, compare
rao_registry.py          (187) # RAORegistry — track computed RAOs
rao_lookup_plots.py      (361) # Plotly: RAO comparison, sensitivity, heatmaps
schematic_generator.py   (519) # Pure SVG: profile, plan, body views
line_generator/
  __init__.py
  line_parser.py         (~320) # Parse hull line definitions
  hull_surface.py        (~350) # B-spline surface interpolation
  panelizer.py           (~380) # Surface → quad panels
  exporter.py            (~230) # Export GDF/DAT/STL
```

### parametric_hull_analysis/ (7 + 1 files, ~1,983 lines)

```
__init__.py               (84) # Package exports (19 symbols)
models.py                (187) # SweepConfig, PassingShipSweepConfig, result dataclasses
sweep.py                 (316) # run_parametric_sweep() — hull variants → BEM → RAOs
forward_speed.py         (346) # DNV-RP-C205 §7.4 encounter frequency + STF corrections
shallow_water.py         (325) # DNV Table 7-1 + PIANC 121 bank effects
passing_ship_sweep.py    (284) # Wang 1975 passing ship force sweeps
charts.py                (441) # Matplotlib: RAO grids, sensitivity, contours
manifest.yaml             (46) # CI traceability → DNV clauses
```
