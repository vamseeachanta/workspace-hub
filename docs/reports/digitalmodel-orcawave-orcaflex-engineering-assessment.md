# digitalmodel OrcaWave / OrcaFlex Engineering Assessment

Updated: 2026-04-02
Produced by: parallel agent team analysis
Traceability: #1639, #1656, #1588, #1638

## 1. OrcaWave Test Coverage (#1639)

### Current state
- 872 test functions across 49 test files
- loguru is NOT a blocker (v0.7.3 installed)

### OrcaWave package (src/digitalmodel/orcawave/)
- 16 non-init source files
- 7 files with dedicated tests (43.8%)
- 9 UNCOVERED files — entire reporting subsystem
  - reporting/builder.py, config.py
  - reporting/sections/ (8 section files)

### Diffraction pipeline (src/digitalmodel/hydrodynamics/diffraction/)
- 51 non-init source files
- 21 files with dedicated tests (41.2%)
- 31 uncovered files across: benchmark subsystem, report builders, CLI, solver/ subpackage

### Combined: 28/69 = 40.6% file-level coverage

### Uplift recommendation
Priority 1: OrcaWave reporting section tests (8 files, zero coverage)
Priority 2: Diffraction benchmark subsystem tests (9 files)
Priority 3: Diffraction report builder tests (6 files)

## 2. OrcaFlex Package Maturity (#1656)

### VERDICT: TESTED — ready for maturity promotion

### Evidence
- 25 source files | 85 classes | 159 functions | 4,983 LOC
- 22/22 non-init modules have matching tests (100% module coverage)
- 260 public API tests + 898 solver-layer tests = 1,158 total
- 98% docstring coverage (223/228 public items)
- All 7 reporting sections covered by test_sections.py (42 tests)
- Every core module has a dedicated test file

### Remaining items for closure
- 5 public functions missing docstrings (code_check_engine.py, pipelay_analysis.py)
- No real `.sim` fixture test yet (#1652 still open, needs licensed-win-1)
- Formal maturity tracker update needed

## 3. Parametric Spec Bridge (#1588)

### Feasibility: CONFIRMED — estimated 2-3 days

### What hull_library provides
- HullProfile (Pydantic, stations-based hull geometry)
- HullParametricSpace (Cartesian-product variant generator)
- HullMeshGenerator (profile → PanelMesh with quad panels)
- MeshScaler with GDF export capability
- HullCatalog for registration and lookup

### What DiffractionSpec needs
- VesselSpec with geometry (mesh_file path), inertia (mass, CoG, radii of gyration)
- EnvironmentSpec, FrequencySpec, WaveHeadingSpec
- All validated by Pydantic

### Specific gaps to bridge
1. MESH FILE PATH (Critical): hull_library produces in-memory PanelMesh; spec needs on-disk .gdf path. Pieces exist but not connected.
2. MASS/INERTIA (Critical): No mass/inertia estimation code exists anywhere. Need ~80 lines of naval architecture empirical formulae.
3. ENVIRONMENT/FREQ/HEADING (Easy): Accept as config params with sensible defaults.
4. SYMMETRY MAPPING (Easy): "y" → SymmetryType.YZ.
5. BATCH ORCHESTRATION (Medium): Loop HullParametricSpace variants through single-hull builder.

### Estimated deliverable
One new bridge module (~300 lines) + tests (~100 lines):
- Mass/inertia estimator from hull dimensions
- Single-hull spec builder (HullProfile → validated spec.yml)
- Parametric batch bridge (HullParametricSpace → N spec.yml files)

### Existing partial bridges
- analysis_setup.py chains hull lookup → mesh generation → scaling (stops before DiffractionSpec)
- mesh_scaler.export_scaled_gdf() handles mesh export
- spec_converter.py is the downstream consumer (spec.yml → solver input)
- Zero existing connections between hull_library and DiffractionSpec

## 4. Reverse Parser Status (#1638)

### Status: IMPLEMENTED — tests already exist

### Evidence
- reverse_parsers.py: 765 lines, both AQWAInputParser and OrcaWaveInputParser
- test_reverse_parsers.py: 775 lines, 33 test functions, 17 test classes
- Tests cover: AQWA round-trip (basic, environment, frequencies, headings, mass, inertia) + OrcaWave round-trip (basic, environment, vessel, frequencies, headings)

### Recommendation
Close #1638 or narrow to residual edge cases only. The issue body implies first-time test creation, but substantial round-trip tests already exist.

## 5. Machine Execution Summary

### Executable on dev-primary now
- #1656 maturity promotion (evidence gathered, ready to close)
- #1638 can be closed or narrowed
- #1639 coverage measurement done; uplift is dev-primary work
- #1588 feasibility confirmed; implementation is dev-primary

### Needs licensed-win-1
- #1652 real .sim fixture
- #1597 RAO extractor with real .owr files
- #1605 integration validation with real artifacts
- #1592 automated handoff with real evidence
- #1264 frame analysis solver validation
- #1292 parachute deployment solver validation

## 6. GTM-Ready Capability Claims

### Can position immediately
- OrcaFlex public API package: TESTED maturity (1,158 tests, 98% docstring coverage)
- DiffractionSpec pipeline: spec.yml → OrcaWave/AQWA conversion (with reverse round-trip)
- Solver queue operations: batch submission, result watching, post-processing hooks
- Hull library: parametric hull generation, mesh export, catalog management

### Needs 2-3 days more work (dev-primary only)
- OrcaWave reporting section test coverage
- Parametric spec bridge connecting hull_library to DiffractionSpec

### Needs licensed machine proof
- Real .sim / .owr artifact-backed integration validation
- OrcaWave → OrcaFlex automated handoff with evidence
- Cross-tool benchmark comparisons
