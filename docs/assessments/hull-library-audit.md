# Hull Library and Parametric Analysis Infrastructure Audit

> Generated: 2026-04-01 | Related: #1567 (Continuous Repo Architecture Intelligence), Wave 2 Task 2.1

## Executive Summary

The hull library and parametric analysis infrastructure is **substantially implemented** — not skeleton code. The codebase contains ~8,500 lines of production Python across 25 modules in `hull_library/` and 8 modules in `parametric_hull_analysis/`, backed by 34 test files. The system covers hull profile definition, mesh generation, parametric scaling, RAO storage, decimation (3 backends), and visualization. Key gaps are: no centralized hull parameter database (L, B, T, Cb registry), only 1 real hull form on file (SkandiNeptune), and no Series 60 or standard hull form coefficients. **Recommendation: extend the existing infrastructure, do not rebuild.**

---

## 1. Hull Library Code Modules

### Location: `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/`

#### Core Data Models

| Module | Lines | Classes | Status | Description |
|--------|-------|---------|--------|-------------|
| `profile_schema.py` | 334 | HullType, HullStation, HullProfile | **Implemented** | Hull shape definition as line profiles (waterlines, sections). Pydantic validation. Save/load YAML. Block coefficient validation. |
| `catalog.py` | 413 | SeaStateDefinition, HullVariation, MotionResponse, HullCatalogEntry, HullCatalog | **Implemented** | Full pipeline: hull→mesh→RAOs→motion response→accelerations. HullCatalog manages registration, mesh generation, spectrum-based motion computation. |
| `parametric_hull.py` | 255 | ParametricRange, HullParametricSpace | **Implemented** | Phase 1 of WRK-043. Cartesian product parametric sweep (L × B × T with configurable linspace). Generates hull variations with unique IDs. |
| `lookup.py` | 376 | HullLookupTarget, HullMatch, HullLookup | **Implemented** | Nearest-neighbour hull form lookup by target vessel dimensions. Scores candidates by normalized distance, returns scaling factors. Sources from both HullCatalog and PanelCatalog. |
| `panel_catalog.py` | 215 | PanelFormat, RaoReference, PanelCatalogEntry, PanelCatalog | **Implemented** | Data models for inventorying hull panel meshes. YAML/CSV serialization. |
| `panel_inventory.py` | 410 | (functions) | **Implemented** | Scans directories for hull panel mesh files (GDF, AQWA DAT, OrcaFlex YAML, metadata-only). Builds full catalog from multiple sources. |
| `analysis_setup.py` | 380 | HullAnalysisInput, HullAnalysisResult | **Implemented** | Chains hull selection→mesh scaling→refinement→RAO linking in a single invocation. |

#### Mesh Generation & Processing

| Module | Lines | Classes / Functions | Status | Description |
|--------|-------|---------------------|--------|-------------|
| `mesh_generator.py` | 505 | MeshGeneratorConfig, HullMeshGenerator | **Implemented** | Converts hull line profiles to PanelMesh via linear interpolation, quad panelization, waterline density refinement. Adaptive X-grid, degenerate panel removal, normal orientation. |
| `mesh_refiner.py` | 388 | MeshQualityMetrics, MeshFamilyMember; refine_mesh, generate_mesh_family | **Implemented** | Mesh subdivision, quality metrics, convergence family generation (multiple panel counts for sensitivity). |
| `mesh_scaler.py` | 313 | ScaleDimensions, ScaleResult; scale_mesh_uniform, scale_mesh_parametric, scale_mesh_to_target | **Implemented** | Uniform, parametric (L/B/T independent), and target-dimension scaling with aspect ratio validation. GDF export. |
| `coarsen_mesh.py` | 391 | DecimationResult; coarsen_mesh | **Implemented** | Unified mesh coarsening dispatcher with QEM and vertex-clustering backends. |
| `decimation.py` | 268 | decimate_mesh | **Implemented** | Pure-NumPy QEM (Garland-Heckbert 1997) mesh decimation. |
| `decimation_gmsh.py` | 233 | remesh_coarsen | **Implemented** | Optional GMSH surface remeshing backend (STL round-trip). |
| `decimation_vtk.py` | 174 | panel_mesh_to_pyvista, decimate_mesh_vtk | **Implemented** | Optional VTK/PyVista decimation backend. |
| `_decimation_helpers.py` | 250 | (geometry helpers) | **Implemented** | Quad-to-tri, plane quadrics, boundary detection, degenerate panel filtering. |

#### RAO Storage & Visualization

| Module | Lines | Classes / Functions | Status | Description |
|--------|-------|---------------------|--------|-------------|
| `rao_database.py` | 293 | RAODatabaseEntry, RAODatabase | **Implemented** | Phase 3 of WRK-043. Store/query RAOs indexed by hull variation parameters. Disk persistence. |
| `rao_registry.py` | 188 | RaoRegistry | **Implemented** | Tracks diffraction analysis results per hull. Registration, lookup, persistence. Links to catalog. |
| `rao_lookup_plots.py` | 362 | per_hull_rao_plot, comparison_plot, parameter_sweep_plot | **Implemented** | Plotly-based interactive RAO visualization. Phase 4 of WRK-043. |
| `schematic_generator.py` | 520 | SchematicGenerator | **Implemented** | SVG profile/plan/body-plan views for hull documentation. |

#### Line Generator Sub-Package

| Module | Lines | Classes | Status | Description |
|--------|-------|---------|--------|-------------|
| `line_generator/__init__.py` | 119 | HullPanelGenerator | **Implemented** | Orchestrator: parse lines → interpolate surface → panelize → export. |
| `line_generator/line_parser.py` | 306 | StationOffset, WaterlineCurve, ProfileCurve, HullLineDefinition, LineParser | **Implemented** | Phase 1. Parses waterline/section/profile data from CSV, JSON, YAML. |
| `line_generator/hull_surface.py` | 304 | HullSurfaceConfig, HullSurface, HullSurfaceInterpolator | **Implemented** | Phase 2. Dense 3D hull surface grid from sparse station data. |
| `line_generator/panelizer.py` | 400 | PanelizerConfig, MeshQuality, Panelizer | **Implemented** | Phase 3. Converts HullSurface to PanelMesh for BEM solvers. |
| `line_generator/exporter.py` | 273 | export_gdf, export_orcawave, export_sections_svg | **Implemented** | Phase 4. GDF (WAMIT), OrcaWave YAML, SVG section views. |

**Hull Library Summary:** 25 Python modules, ~8,100 lines total. All modules are **implemented** (not stubs). No NotImplementedError found. No TODO/FIXME markers found.

---

## 2. Parametric Hull Analysis Package

### Location: `digitalmodel/src/digitalmodel/hydrodynamics/parametric_hull_analysis/`

| Module | Lines | Key Contents | Status | Description |
|--------|-------|-------------|--------|-------------|
| `__init__.py` | 85 | — | Orchestration | Package docstring: sweeps hull forms through BEM solvers, forward speed, passing ship, shallow water. |
| `models.py` | 188 | DepthClassification, BankSlopeType, SweepConfig, PassingShipSweepConfig, SweepResultEntry, PassingShipSweepEntry, BankEffectResult | **Implemented** | Full data models with Pydantic. classify_depth() for shallow/intermediate/deep classification. |
| `sweep.py` | 317 | run_parametric_sweep, sweep_to_dataframe | **Implemented** | Core sweep: generates hull variants via hull_library, runs BEM via Capytaine, collects RAOs into RAODatabase. |
| `charts.py` | 442 | rao_comparison_grid, parameter_sensitivity_plot, depth_sensitivity_plot, passing_ship_contour, operability_chart | **Implemented** | Matplotlib parametric plots for analysis results. |
| `forward_speed.py` | 347 | wave_number, encounter_frequency, correct_rao_for_speed, strip_theory_speed_correction | **Implemented** | DNV-RP-C205 §7.4 encounter frequency + strip-theory corrections. |
| `shallow_water.py` | 326 | dnv_shallow_water_factor, pianc_bank_suction_force, pianc_bank_clearance_width | **Implemented** | DNV-RP-C205 Table 7-1 + PIANC 121 bank effects. |
| `passing_ship_sweep.py` | 285 | run_passing_ship_sweep, pianc_operability_check | **Implemented** | Parametric passing ship force sweep (Wang 1975 slender-body theory). |
| `manifest.yaml` | ~20 | CI/website traceability | **Config** | Module metadata, primary standard: DNV-RP-C205 (2021). |

**Parametric Analysis Summary:** 8 files, ~2,000 lines total. All modules are **implemented**. Standard-linked (DNV-RP-C205). Integrates with Capytaine BEM (#1440, #1464).

---

## 3. Existing Hull Data

### 3.1 Hull Forms Directory
**Path:** `digitalmodel/docs/domains/orcawave/hull_forms/`

| File | Hull | Type | Key Parameters |
|------|------|------|----------------|
| `NeptuneBatchTestCase.yml` | SkandiNeptune (LC08) | OrcaFlex vessel model | L=96.6m, Mass=9,196te, Draft=5.551m, CoG=[0,0,3.309], 7 RAO directions (0°–105°), 30 periods (1–30s), Full 6-DOF RAOs |

This is a complete OrcaFlex vessel type definition with full RAO tables, not an OrcaWave input.

### 3.2 Hull Library Documentation
**Path:** `digitalmodel/docs/domains/hull_library/`

| File | Content |
|------|---------|
| `hull_scaling_guide.md` | 148-line guide covering uniform and parametric (L/B/T independent) mesh scaling, re-panelization guidelines, and API examples. References HullCatalog, HullVariation, HullMeshGenerator, MeshGeneratorConfig. |

### 3.3 Spec.yml Files (13 Total)

#### L00: WAMIT Validation Cases (10 files)

| Case | Vessel Name | Type | Mesh | Analysis Type | Notes |
|------|------------|------|------|---------------|-------|
| 2.1 | Test01_cylinder | cylinder | val_cylinder_r1_t05.gdf | diffraction | Single body, infinite depth, xz+yz symmetry |
| 2.2 | Test01_cylinder | cylinder | val_cylinder_r1_t05.gdf | diffraction | Same as 2.1 (different frequency set) |
| 2.3 | Test01_cylinder | cylinder | val_cylinder_r1_t05.gdf | diffraction | Inclined body (15° roll, z-offset 0.27) |
| 2.6 | test05_cylinder + test05_spheroid | cylinder + ellipsoid | val_cylinder_r1_t2.gdf + val_spheroid.gdf | diffraction | Multi-body case |
| 2.7 | Pyramid_ZC08 | custom | pyramid_zc08.gdf + .csf | diffraction | No symmetry, control surface, 18 headings |
| 2.8 | Ellipsoid_96p | custom | ellipsoid_96p.gdf + .csf | diffraction | Control surface, 18 headings, single period |
| 2.9 | cylinder with moonpool | moonpool_cylinder | val_moonpool_body.gdf | diffraction | Moonpool geometry |
| 3.1 | bottom mounted cylinder | bottom_mounted_cylinder | val_bmc.gdf | full_qtf | All DOFs fixed, finite depth (1m), QTF |
| 3.2 | Sphere_R5 | custom | sphere_r5.gdf | diffraction | Sphere validation |
| 3.3 | (see file) | — | — | — | Additional validation case |

#### L01–L04: Engineering Benchmarks

| Case | Vessel Name | Type | Mass | Mesh Format | Analysis | Key Parameters |
|------|------------|------|------|-------------|----------|----------------|
| L02 | Barge_Benchmark | barge | 16,400 te | GDF | diffraction | 200m depth, 15 periods (5.2–12.6s) |
| L03 | Body1 (ship) | ship | 9,017.95 te | DAT (AQWA) | full_qtf | 500m depth, CoG=[2.53,0,-1.974], external roll damping |
| L04 | Spar_Benchmark | spar | 55,000 te | DAT (AQWA) | diffraction | 200m depth, CoG=[0,0,-61.63], rad/s input |

### 3.4 OrcaWave Examples (L01–L06+)

| Example | Type | Contents |
|---------|------|----------|
| L01_default_vessel | Default vessel | .yml, .owr, .gdf, control surface, license test scripts, API execution scripts |
| L02 OC4 Semi-sub | Floating wind | Semi-submersible mesh, OrcaWave workspace, run script |
| L03 Semi-sub multibody | Multi-body | Centre column + outer column meshes + control surfaces |
| L04 Sectional bodies | Sectional | Pontoon + keystone + column, static/dynamic workspaces |
| L05 Panel pressures | Pressures | Pontoon + keystone + column, panel pressure extraction |
| L06 Full QTF | QTF | Full QTF diffraction analysis |
| qa/ | Quality assurance | QA results JSON for L01–L06, QA report, QA runner script |

---

## 4. Test Coverage

### Hull Library Tests (34 files)

**Path:** `digitalmodel/tests/hydrodynamics/hull_library/`

| Test File | Module Under Test |
|-----------|-------------------|
| test_catalog.py | catalog.py |
| test_catalog_additional.py | catalog.py (extended) |
| test_lookup.py | lookup.py |
| test_parametric_hull.py | parametric_hull.py |
| test_profile_schema.py | profile_schema.py |
| test_rao_database.py | rao_database.py |
| test_rao_registry.py | rao_registry.py |
| test_rao_lookup_plots.py | rao_lookup_plots.py |
| test_schematic_generator.py | schematic_generator.py |
| test_mesh_generator.py | mesh_generator.py |
| test_mesh_refiner.py | mesh_refiner.py |
| test_mesh_scaler.py | mesh_scaler.py |
| test_panel_catalog.py | panel_catalog.py |
| test_panel_inventory.py | panel_inventory.py |
| test_decimation.py | decimation.py |
| test_decimation_gmsh.py | decimation_gmsh.py |
| test_decimation_vtk.py | decimation_vtk.py |
| test_coarsen_mesh.py | coarsen_mesh.py |
| test_analysis_setup.py | analysis_setup.py |
| test_integration.py | Cross-module integration |
| test_panel_integration.py | Panel workflow integration |
| test_hull_library_expansion.py | Expansion features |
| test_seed_data.py | Seed data validation |
| line_generator/test_line_parser.py | line_parser.py |
| line_generator/test_hull_surface.py | hull_surface.py |
| line_generator/test_panelizer.py | panelizer.py |
| line_generator/test_exporter.py | exporter.py |

**Additional:** `tests/unit/hull_library/test_catalog_extended.py`, `test_hull_parametric.py`

**Coverage assessment:** Every hull_library module has at least one dedicated test file. Integration tests exist. This is well-tested code.

---

## 5. Related GitHub Issues

### #1314 — WRK-1372: Ship-specific hydrostatic data tables (DDG-51, FFG-7)
- **Status:** OPEN
- **Labels:** wrk-item, machine:dev-primary
- **Body:** Auto-created by backfill-github-refs.sh (no detailed spec)
- **Relevance:** Needs ship-specific hull data (DDG-51 destroyer, FFG-7 frigate). These are military hull forms — no public hull line plans. Would require parametric approximation from published principal dimensions.

### #1319 — WRK-1377: Hull form parametric design — coefficients and Series 60
- **Status:** OPEN
- **Labels:** wrk-item, machine:dev-primary
- **Body:** Auto-created by backfill-github-refs.sh (no detailed spec)
- **Relevance:** Series 60 is the Todd (1963) standard systematic hull form series. Implementing this requires digitizing the Series 60 offsets table (publicly available in "Principles of Naval Architecture" Vol. III) and integrating with the existing `parametric_hull.py` and `HullProfile` schema. This would be the single most impactful addition to the hull library.

### Related Issues (from search)
- **#22** — WRK-043: Parametric hull form analysis with RAO generation (the parent issue for hull_library)
- **#1464** — Capytaine BEM available for hull mesh wave load analysis
- **#1440** — Install Capytaine BEM solver into ACE ecosystem
- **#14** — WRK-1251: FreeCAD deep parametric engineering — hull generation
- **#29** — WRK-099: Run 3-way benchmark on Unit Box hull
- **#1297** — WRK-1382: Naval architect expert skill

---

## 6. Gap Analysis: Implemented vs. Skeleton vs. Gap

### Fully Implemented (Production-Ready)
- Hull profile schema (HullProfile, HullStation) with YAML persistence
- Mesh generation from hull lines (HullMeshGenerator)
- Mesh scaling (uniform, parametric, target-dimension)
- Mesh decimation/coarsening (3 backends: pure-NumPy QEM, GMSH, VTK)
- Mesh refinement and convergence family generation
- Panel catalog and inventory scanning (GDF, AQWA DAT, OrcaFlex YAML)
- Hull lookup by target dimensions (nearest-neighbour matching)
- RAO database (store, query, persist)
- RAO registry (per-hull result tracking)
- Parametric hull space definition and combination generation
- Line generator pipeline (parse → interpolate → panelize → export)
- Schematic generation (SVG profile/plan/body-plan views)
- Visualization (Plotly RAO plots, comparison, parameter sweep)
- Parametric sweep orchestration (Capytaine-based)
- Forward speed corrections (DNV-RP-C205)
- Shallow water corrections (DNV-RP-C205 + PIANC 121)
- Passing ship force sweep (Wang 1975)
- Charts (RAO grids, sensitivity, operability)

### Partially Implemented
- Hull catalog **has infrastructure** but only 1 real hull form (SkandiNeptune) — needs seed data
- RAO database **schema exists** but no populated database of results
- Panel inventory scanning **works** but the actual mesh file inventory in `data/hull_library/panels/` needs cataloging

### Gaps (Not Yet Built)
1. **Centralized hull parameter database** — No L, B, T, Cb registry across all hull forms. Each spec.yml defines vessel parameters inline. Need a `hull_registry.yaml` or similar.
2. **Series 60 hull form coefficients** — #1319 is open. The parametric_hull module can generate variations, but it lacks standard hull form series data (Series 60, DTMB, Wigley).
3. **Ship-specific hydrostatic tables** — #1314 open. DDG-51, FFG-7 data not available.
4. **Parametric spec.yml generator** — The DiffractionSpec pipeline validates spec.yml files, and parametric_hull generates hull variations, but no automated bridge from "sweep definition" → "N validated spec.yml files".
5. **Hull form seed data** — Only 1 hull form on file (SkandiNeptune, which is an OrcaFlex vessel type, not a hull line definition). Need barge, ship, spar, semi-sub reference hull lines.
6. **RAO extraction from OrcaWave results** — The RAO database exists but no OrcaWave .owr parser populates it. Need extractor that reads OrcaWave results and stores in RAODatabase.
7. **Capytaine-hull_library integration glue** — sweep.py references Capytaine but issues #1440 and #1464 suggest the integration is not yet operational.

---

## 7. Recommendation

**Extend the existing hull_library — do not rebuild.**

The infrastructure is mature (8,500+ lines, 34 test files, clean architecture). The gaps are **data gaps** and **pipeline glue**, not architecture gaps:

1. **Seed the hull registry** — Add 5–10 standard hull forms (barge, tanker, semi-sub, spar, FPSO) as HullProfile YAML files in `data/hull_library/profiles/`. Each needs L, B, T, Cb, station offsets.

2. **Implement Series 60** (#1319) — Digitize Series 60 offsets (Cb = 0.60, 0.65, 0.70, 0.75, 0.80) as HullProfile entries. This single addition enables meaningful parametric sweeps.

3. **Build parametric spec.yml generator** — Small module (~200 lines) that takes a sweep YAML, calls HullParametricSpace.combinations(), generates DiffractionSpec-compliant spec.yml per variation.

4. **Build RAO extraction bridge** — Script that reads .owr results → RAODatabase entries. ~100 lines on the licensed machine.

5. **Create hull_registry.yaml** — Single source of truth listing all known hull forms with principal dimensions, mesh file paths, and RAO database entries.

The architecture supports all of this — the classes, schemas, and pipelines are already there. The work is filling in data and connecting existing pieces.
