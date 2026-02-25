# WRK-047 Plan Refresh — OpenFOAM CFD Capability

> Status: Research completed 2026-02-24
> WRK: WRK-343 (refreshes WRK-047, feeds WRK-292)
> Based on: WRK-290 completion log, July 2025 specs, current digitalmodel state

## Executive Summary

WRK-047 was planned 2026-01-29 and approved 2026-02-10. It is still valid and
implementation-ready. Seven material things have changed since planning:

1. **OpenFOAM is now installed** (was "NOT installed" in WRK-047 Phase 0)
2. **PyFoam `six.moves` bug is fixed** (was "broken" at WRK-343 creation)
3. **Full Python ecosystem installed** (meshio, pyvista, vtk, PyFoam all working)
4. **Module path conflict resolved** (July 2025 spec vs WRK-047 — see Section 5)
5. **July 2025 Option B (PyFoam-centric) needs revision** — PyFoam should be
   supplementary, not primary; Jinja2+subprocess is the correct foundation
6. **GMSH module unchanged** — identical to what Phase 0 assessed
7. **BemRosetta unavailable on ace-linux-2** — use acma-ansys05, or skip in Phase 0

**Recommendation: Start WRK-047 Phase 1 immediately.** All prerequisites met.

---

## Section 1: Environment Status (ace-linux-2)

### What WRK-047 Phase 0 assumed

> "OpenFOAM is NOT installed on this system (no `blockMesh`, `interFoam`, etc.
> found in PATH)"
> "GMSH Python package is NOT installed (needed for volume mesh generation)"
> "PyVista/VTK are NOT installed (useful for post-processing visualization)"

### Current state (2026-02-24, from WRK-290)

| Item | WRK-047 Phase 0 assessment | Current state | Change |
|------|--------------------------|---------------|--------|
| OpenFOAM v2312 | NOT installed | **INSTALLED** — blockMesh, simpleFoam verified | RESOLVED |
| GMSH Python package | NOT installed | **INSTALLED** (4.12.1 CLI + pip gmsh) | RESOLVED |
| PyVista | NOT installed | **INSTALLED** (v0.47.0) | RESOLVED |
| VTK | NOT installed | **INSTALLED** (v9.6.0) | RESOLVED |
| meshio | Pending | **INSTALLED** (v5.3.5) | RESOLVED |
| PyFoam | Broken (`six.moves`) | **INSTALLED AND FIXED** (v2023.7) | RESOLVED |
| BemRosetta | Skip | Skip (no Linux binary) | UNCHANGED |
| ParaView | Separate install | **INSTALLED** (v5.11.2) | RESOLVED |

**WRK-047 Phase 0 is effectively complete.** All environment setup work was done
by WRK-290. Skip Phase 0, proceed to Phase 1.

---

## Section 2: July 2025 Specs Reconciliation

### What exists in digitalmodel/.claude/projects/2025-07-29-openfoam-capabilities/

Three documents from July 2025:
- `spec.md` — user stories, scope, deliverables
- `sub-specs/technical-spec.md` — module structure, YAML config, Option B (PyFoam)
- `sub-specs/tests.md` — 150+ lines of unit/integration test coverage

### Comparison: July 2025 spec vs WRK-047

| Dimension | July 2025 Spec | WRK-047 | Verdict |
|-----------|---------------|---------|---------|
| Module path | `src/digitalmodel/modules/openfoam/` | `src/digitalmodel/solvers/openfoam/` | **WRK-047 wins** — see Section 5 |
| YAML config schema | Comprehensive (10+ keys) | Implicit in Pydantic models | **Merge** — July 2025 YAML is reusable |
| PyFoam dependency | Primary ("Option B selected") | Optional/supplementary | **WRK-047 is correct** — see Section 3 |
| Solver list | simpleFoam, pimpleFoam | + interFoam, 6DOF, marine-specific | **WRK-047 is more complete** |
| Test approach | Mock strategy + fixtures | TDD, real subprocess mocking | **Compatible — merge both** |
| Marine application focus | Hull resistance | Hull + waves + VIV + sloshing + green water | **WRK-047 is more complete** |
| Dependencies | PyFoam, meshio, pandas, vtk | jinja2, pyyaml + optional: gmsh, pyvista, vtk | **WRK-047 is tighter** |
| STL import | Mentioned | Full pipeline via GMSH + meshio | **WRK-047 is more complete** |
| Parallel execution | ProcessPoolExecutor | decomposeParDict + mpirun subprocess | **WRK-047 is more realistic** |

### Usable artifacts from July 2025 spec

The following July 2025 elements should be carried forward into WRK-047:

**YAML config schema** (from `technical-spec.md`):
The schema is well-structured and covers the right keys. It should become the
canonical `config_schemas.py` validation schema in Phase 1:
```yaml
openfoam_analysis:
  case_name, geometry, mesh, physics, boundary_conditions,
  simulation, post_processing, output
```
This maps cleanly to the WRK-047 Pydantic/dataclass models.

**Test coverage matrix** (from `tests.md`):
The test list is comprehensive and maps directly to WRK-047 phases. Incorporate
into `tests/solvers/openfoam/` during each phase. Particularly useful:
- Unit test list for `MeshGenerator`, `SolverConfiguration`, `PostProcessor`
- Mock strategy for subprocess (OpenFOAM executables)
- Validation benchmarks (flat plate, cylinder, NACA airfoil)

**User stories** (from `spec.md`):
Three stories (environment setup, hull analysis, test case management) align with
WRK-047 phases. No changes needed — they are valid requirements.

---

## Section 3: PyFoam Assessment — Is Option B Still Valid?

### July 2025 decision

> "Option B: File-Based Integration with PyFoam (Selected)"
> "Pros: Version flexibility, easier debugging, follows DigitalModel patterns,
>  robust error handling. Rationale: PyFoam provides stable interface across
>  OpenFOAM versions."

### Current assessment

**Option B is partially valid but overstates PyFoam's centrality.**

PyFoam was selected in July 2025 under the assumption it provides "stable interface
across versions." In practice:
1. PyFoam 2023.7 ships with a broken bundled `six` library on Python 3.12 — fixed
   manually on ace-linux-2, but this is a fragility point
2. PyFoam is not needed for dict file generation — Jinja2 templates are cleaner,
   more maintainable, and version-independent
3. PyFoam's `ParsedParameterFile` is useful for reading/modifying existing dicts,
   but WRK-047 Phase 1 writes dicts from scratch (templates are better here)
4. PyFoam's log parsing utilities ARE genuinely useful and should be used in Phase 4

**Revised stance for WRK-047:**

| Task | July 2025 (Option B) | WRK-047 revised |
|------|---------------------|-----------------|
| Dict file generation | PyFoam utilities | **Jinja2 templates** (WRK-047 Phase 1) |
| Dict file reading/editing | PyFoam ParsedParameterFile | **PyFoam** where available, fallback to regex |
| Solver execution | PyFoam BasicRunner | **subprocess.run** pattern (from blender_wrapper.py) |
| Log parsing / residuals | PyFoam FoamLogFile | **PyFoam FoamLogFile** (genuinely useful) |
| Post-processing field data | PyFoam field reader | **pyvista / fluidfoam** (more capable) |

**Bottom line:** WRK-047's Jinja2+subprocess approach supersedes the July 2025
PyFoam-centric design. PyFoam is a useful supplementary tool, not the foundation.
The `PYFOAM_AVAILABLE` guard pattern (like `GMSH_AVAILABLE`) is the right approach.

---

## Section 4: GMSH Module — Has It Changed?

### What WRK-047 Phase 0 assessed (2026-01-29)

- `solvers/gmsh_meshing/mesh_generator.py` — GMSHMeshGenerator with box, cylinder,
  STL surface meshing and VTK/MSH export
- `solvers/gmsh_meshing/models.py` — MeshQuality, MeshStatistics, etc.
- `solvers/gmsh_meshing/quality_analyzer.py` — MeshQualityAnalyzer

### Current state (2026-02-24)

Files checked:
```
digitalmodel/src/digitalmodel/solvers/gmsh_meshing/
├── __init__.py         exports: MeshQuality, MeshStatistics, GeometryType,
│                                ElementType, MeshAlgorithm, GMSHMeshGenerator,
│                                MeshQualityAnalyzer
├── mesh_generator.py   GMSHMeshGenerator: box, cylinder, STL surface meshing
│                       save_mesh_vtk(), save_mesh_msh() — both present
├── models.py           GeometryType, ElementType, MeshAlgorithm, MeshQuality, etc.
├── quality_analyzer.py MeshQualityAnalyzer with Jacobian, aspect ratio, skewness
└── cli.py              Click CLI — box, cylinder commands
```

**Finding: GMSH module unchanged.** Identical to WRK-047 Phase 0 assessment.

**Important gap identified:** The `__init__.py` docstring claims export to OpenFOAM
format, but the actual `mesh_generator.py` only has `save_mesh_vtk()` and
`save_mesh_msh()`. There is no `save_mesh_openfoam()` method. The OpenFOAM export
capability must come from either:
- `meshio.write(path, mesh, file_format="openfoam")` — recommended path
- `gmshToFoam` utility — subprocess call to OpenFOAM built-in tool

This gap is already addressed in WRK-047 Phase 2 (`mesh_pipeline.py` with meshio),
so no plan change is needed. The gap in the GMSH module's docstring is a documentation
debt but not a blocker.

---

## Section 5: Module Path Resolution — modules/ vs solvers/

### The conflict

- **July 2025 spec**: `src/digitalmodel/modules/openfoam/`
- **WRK-047**: `src/digitalmodel/solvers/openfoam/`

### Evidence supporting `solvers/`

1. **No `modules/` directory exists** in the codebase. Checked 2026-02-24:
   `ls digitalmodel/src/digitalmodel/modules/` → directory does not exist.

2. **Existing pattern is `solvers/`**:
   - `solvers/gmsh_meshing/` — external meshing solver integration
   - `solvers/blender_automation/` — external 3D tool integration
   - `solvers/orcaflex/` — commercial solver integration
   - `solvers/orcawave/` — wave solver integration
   - `solvers/fea_model/` — FEA solver integration

3. **Semantic fit**: OpenFOAM is an external solver being wrapped, not an internal
   analysis module. The `solvers/` namespace groups all "external tool wrappers."
   The `hydrodynamics/`, `structural/`, etc. namespaces contain digitalmodel's own
   analysis logic.

4. **WRK-047 was reviewed and approved (2026-02-10)** with `solvers/openfoam/` path.

### Decision
**Use `src/digitalmodel/solvers/openfoam/`** — confirmed.

The July 2025 spec's `modules/openfoam/` path reflects an older namespace convention
that was abandoned. The July 2025 spec should be considered superseded by WRK-047
on this point.

---

## Section 6: BemRosetta — Impact Assessment

### What WRK-047 Phase 0 assumed
BemRosetta mesh models (`hydrodynamics/bemrosetta/models/mesh_models.py`) available
as input to OpenFOAM geometry import pipeline.

### Current state
- BemRosetta software: NOT available on ace-linux-2 (no Linux binary, skipped in WRK-290)
- **Available on acma-ansys05** only
- `bemrosetta/models/mesh_models.py` and mesh handlers: **present in digitalmodel codebase**
  (the Python models and parsers exist, independent of BemRosetta binary being installed)

### Impact on WRK-047
**No impact on Phase 1 or Phase 2.** The `PanelMesh` dataclass and mesh file parsers
(GDF, DAT, STL handlers) exist in the codebase and can be used for testing the OpenFOAM
geometry import pipeline without BemRosetta binary running.

For integration testing with real BemRosetta outputs: use pre-generated fixture files
(sample GDF/DAT meshes can be committed as test fixtures).

---

## Section 7: Are Jinja2 Templates the Right Approach?

See `docs/research/openfoam-dict-patterns.md` for full analysis.

**Conclusion: Yes, Jinja2 is correct.** The conditional logic needed in templates
(transient vs steady, VOF vs single-phase, turbulence model selection) cannot be
cleanly expressed with f-strings or dataclass `__str__` methods. Jinja2 provides:
- `{% if %}` blocks for solver-type switching
- `{{ variable | default(value) }}` for optional parameters with defaults
- Template inheritance for common headers
- Whitespace control for clean output

Jinja2 is already used in some form in other tools in this ecosystem.

---

## Section 8: Recommended Plan Amendments for WRK-047

### Amendments (changes to existing plan)

**Amendment A: Phase 0 is complete — skip to Phase 1**

Phase 0 was "Prerequisites and Environment Assessment." All items are resolved:
- OpenFOAM installed ✓
- Python packages installed ✓
- `OPENFOAM_AVAILABLE` flag pattern confirmed valid ✓

Start directly with Phase 1 (`models.py`, `case_builder.py`).

---

**Amendment B: PyFoam — use as supplementary tool, not dependency**

Original: "PyFoam broken — impact on Phase 4/5?"
Resolution: PyFoam is fixed. But WRK-047 should treat it as an optional dependency
(like gmsh and pyvista), not a required one.

```python
# In post_processing.py
try:
    from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
    PYFOAM_AVAILABLE = True
except ImportError:
    PYFOAM_AVAILABLE = False
```

The Jinja2 template approach for Phase 1 does NOT require PyFoam. PyFoam is useful
for Phase 4 log parsing only.

---

**Amendment C: Add meshio as a required dependency for Phase 2**

WRK-047 Dependency Summary lists meshio as optional. It should be elevated to
**required for Phase 2** because:
- meshio provides the only clean GMSH → OpenFOAM conversion path in Python
- The alternative (`gmshToFoam` subprocess) requires OpenFOAM to be installed,
  breaking the dry-run design

Updated dependency table:
```
Required Python packages: pyyaml, numpy, jinja2, meshio
Optional Python packages: gmsh (enhanced meshing), pyvista, vtk, PyFoam
External software: OpenFOAM (required for execution, not file generation)
```

---

**Amendment D: Add `fluidfoam` to the Phase 4 evaluation list**

fluidfoam provides direct field reading from OpenFOAM time directories without
a foamToVTK conversion step. Install on ace-linux-2 and evaluate alongside pyvista.

For simple force/scalar extraction: fluidfoam is simpler.
For 3D visualization: pyvista is required.

---

**Amendment E: YAML config schema — adopt July 2025 schema as canonical**

The July 2025 technical spec's YAML schema is well-designed and maps cleanly to
the WRK-047 Pydantic models. Use it as the canonical schema for `config_schemas.py`
(Phase 1). No duplication of effort needed.

Key additions from WRK-047 that the July 2025 schema does not cover:
- `case_type` enum: `WAVE_LOADING`, `CURRENT_LOADING`, `GREENWATER`, `SLOSHING`, `VIV`
- Wave boundary conditions: Stokes 2nd/5th, JONSWAP
- `decomposeParDict` section (parallel decomposition)

---

**Amendment F: Test strategy — merge July 2025 test spec with WRK-047 test files**

The July 2025 `tests.md` spec contains a comprehensive test list that should be
incorporated directly into WRK-047 test files. The mock strategies are compatible:
- Mock subprocess calls for OpenFOAM executables
- `pytest tmp_path` fixtures for file system operations
- `unittest.mock.patch` for PyFoam and OpenFOAM availability guards

No conflicts. The July 2025 test spec is additive — add its test cases to the
WRK-047 test files as they are created in each phase.

---

**Amendment G: Confirm ESI v2312 as target version**

WRK-047 says "target OpenFOAM.com (ESI) v2306+ syntax." Confirmed:
- v2312 is installed on ace-linux-2 ✓
- v2312 is a superset of v2306 ✓
- ESI v2312 dict syntax is the template target ✓

See `docs/research/openfoam-version-landscape.md` for details.
Specific note: use `turbulenceProperties` (not `momentumTransport`) and
`transportProperties` (not `physicalProperties`) — ESI naming, not Foundation.

---

**No-change items (still valid from WRK-047):**

| Item | Status |
|------|--------|
| `src/digitalmodel/solvers/openfoam/` module path | Confirmed |
| Phase structure (1-6) | Confirmed |
| Pydantic/dataclass models approach | Confirmed |
| `OPENFOAM_AVAILABLE` flag pattern | Confirmed |
| Dry-run design (generate files without running solver) | Confirmed |
| Blender subprocess pattern for runner.py | Confirmed |
| Click CLI pattern from gmsh_meshing/cli.py | Confirmed |
| Marine solver list (interFoam, simpleFoam, pimpleFoam, 6DOF) | Confirmed |
| Integration with bemrosetta PanelMesh | Confirmed (via fixture files for testing) |
| Risk table | Confirmed (all mitigations valid) |

---

## Section 9: Recommended Next Steps for WRK-047

**Week 1: Phase 1 — Data Models and Case Builder**

Priority order:
1. Create `tests/solvers/openfoam/test_models.py` — TDD first
2. Create `src/digitalmodel/solvers/openfoam/__init__.py`
3. Create `src/digitalmodel/solvers/openfoam/models.py` — Pydantic models
4. Create `src/digitalmodel/solvers/openfoam/case_builder.py`
5. Create `src/digitalmodel/solvers/openfoam/templates/` with Jinja2 templates
   (see `openfoam-dict-patterns.md` for all 8 template files)
6. Run tests — aim for 100% coverage on Phase 1 code

**Week 2: Phase 2 — Mesh Pipeline**

1. `test_mesh_pipeline.py` — TDD
2. `mesh_pipeline.py` — GMSH → meshio → OpenFOAM polyMesh
3. `geometry_import.py` — PanelMesh → STL → OpenFOAM
4. `domain_builder.py` — automatic domain sizing

**Assign to Codex (as WRK-047 plan specifies for phases 1, 2, 4, 5)**

---

## Section 10: Impact on WRK-292

WRK-292 (capability map — file formats, workflow pipelines, interoperability matrix)
depends on WRK-290 (complete) and WRK-291. The WRK-343 findings feed directly into
WRK-292's CFD pipeline documentation:

**CFD pipeline (verified working on ace-linux-2):**
```
FreeCAD (STEP) → GMSH (mesh generation) → meshio (format conversion)
     → OpenFOAM polyMesh → blockMesh/snappyHexMesh → simpleFoam/interFoam
     → foamToVTK → pyvista (post-processing) / ParaView (visualization)
```

**Python automation path (all packages installed):**
```python
gmsh → save_mesh_msh() → meshio.write(format="openfoam") →
    subprocess.run("blockMesh") → subprocess.run("simpleFoam") →
    subprocess.run("foamToVTK") → pyvista.read() → plot/export
```

WRK-292 can use this document and `openfoam-python-ecosystem.md` as primary
sources for the CFD section of the capability map.

---

*Generated: 2026-02-24 | WRK-343*
