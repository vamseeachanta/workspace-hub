# WRK-1251 Resource Pack

## Existing Assets

### FreeCAD Integration
- `digitalmodel/src/digitalmodel/visualization/design_tools/freecad_integration.py` (441 lines) — FreeCADWorkflow: pressure vessel, piping, export (STEP/STL/OBJ). No hull generation.
- `digitalmodel/src/digitalmodel/visualization/design_tools/ai_cad_agent.py` (736 lines) — NL-to-CAD agent
- Skill: `.claude/skills/engineering/cad/freecad-automation/SKILL.md` v1.0.0
- FreeCAD 0.21.2 installed on ace-linux-2 via `freecadcmd` (headless, FreeCADGui stub)

### Hull Library (Panel Mesh — NOT CAD solids)
- `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/` — BSpline surface interpolation → panelization → GDF/OrcaWave/SVG export
- `hull_library/parametric_hull.py` — Cartesian product scaling (24 tests)
- `hull_library/rao_database.py` — Parquet RAO storage (22 tests)
- `hull_library/rao_lookup_plots.py` — Plotly visualization (16 tests)
- Total: 62 passing tests across hull library

### Naval Architecture / Hydrostatics
- `digitalmodel/src/digitalmodel/naval_architecture/hydrostatics.py` — buoyancy, CG, GM (USNA EN400 validated)
- `naval_architecture/fundamentals.py` — unit conversions, water density
- `naval_architecture/stability.py`, `resistance.py`, `curves_of_form.py`

### Gmsh Meshing
- `digitalmodel/src/digitalmodel/solvers/gmsh_meshing/` — mesh generation, quality analysis, multi-format export
- 15 test files, active status
- Gmsh 4.15.1 (pip), 4.12.1 (system binary)
- Skill: `.claude/skills/engineering/cad/gmsh-meshing/SKILL.md` (1,093 lines)

### Pipelines
- `scripts/pipelines/gmsh_openfoam_orcaflex.py` — multi-physics pipeline (gmsh→OpenFOAM→OrcaFlex)
- Skill: `.claude/skills/engineering/workflows/gmsh-openfoam-orcaflex/SKILL.md`

## Gaps (What WRK-1251 Must Build)

| Component | Gap | Existing Foundation |
|-----------|-----|-------------------|
| FreeCAD NURBS hull | No CAD solid hull generation | hull_library has panel mesh only |
| FreeCAD hydrostatics | No FreeCAD-based hydrostatic computation | naval_architecture/hydrostatics.py exists for manual calc |
| CalculiX FEM chain | Not installed, zero integration | gmsh can export Abaqus INP format |
| FEM boundary conditions | No BC/material/load abstraction | OrcaFlex FEA only (slender structures) |
| Design table orchestration | No batch FreeCAD+FEM runner | parametric_hull.py does scaling only |
| Round-trip validation | No CAD→STEP→gmsh→solver pipeline | Individual pieces exist but not chained |
| STEP export from hull | freecad_integration.py has STEP export but not for hulls | Export infrastructure ready |

## Prior Work Items

| WRK | Title | Status | Relevance |
|-----|-------|--------|-----------|
| WRK-048 | Blender working configurations | pending | Complementary CAD/viz |
| WRK-611 | FCStd parser for AI-agent geometry extraction | done | Can read FreeCAD files without runtime |
| WRK-612 | Gmsh Python API for hull mesh | done | Gmsh meshing pipeline for curved hulls |
| WRK-614 | FreeCAD FEM workbench evaluation | done | 36/36 checks passing |
| WRK-1249 | Gmsh deep meshing workflows | pending | Depends on WRK-140 |
| WRK-1252 | Full CAD-to-CFD pipeline | pending | Blocked by WRK-1251 |

## Software Versions (ace-linux-2)

- FreeCAD 0.21.2: `freecadcmd` (headless)
- Gmsh 4.15.1 (pip) / 4.12.1 (system)
- OpenFOAM v2312: `/usr/lib/openfoam/openfoam2312/`
- ParaView 5.11.2 (SIGSEGV on import — use VTK 9.6.0 fallback)
- CalculiX: **NOT INSTALLED** — must install `ccx` before FEM chain work

## Key Constraints

1. CalculiX installation required before FEM chain implementation
2. FreeCAD 0.21.2 Part.BSplineSurface API available for NURBS hull generation
3. All operations must be headless (freecadcmd, no GUI)
4. Hydrostatic validation against analytical (2% tolerance per AC)
5. FEM validation: plate with hole Kt ≈ 3.0 (5% tolerance per AC)
