# WRK-1251: FreeCAD Deep Parametric Engineering — Feature Plan

## Context

FreeCAD is the only open-source parametric CAD tool in the stack. WRK-1251 adds production-grade hull generation, FEM structural analysis via CalculiX, and design table batch studies — capabilities that currently require commercial licenses (ANSYS on licensed-win-1). This unlocks WRK-1252 (full CAD-to-CFD pipeline).

**Classified as Feature WRK** because it exceeds chunk-sizing on 3 dimensions: 2 repos (max 1), 10+ files (max 5), 4 components (max 3 phases).

## Key Design Decisions

1. **New module, not hull_library extension** — FreeCAD hull generator lives in `visualization/design_tools/freecad_hull.py`, consuming `HullProfile` from hull_library's schema. Keeps panel mesh pipeline (hydrodynamics) separate from CAD solid pipeline (FreeCAD).

2. **CalculiX install = prerequisite step in FEM child**, not a separate WRK. It's one `apt install` command, not a multi-file engineering task.

3. **Skill update = separate child WRK** targeting workspace-hub repo (different repo from implementation children targeting digitalmodel).

4. **Process-level parallelism for design tables** — FreeCAD is not thread-safe; each batch variation runs in a separate process via `multiprocessing.Pool`.

## Decomposition: 5 Children

```
Child A (Hull + Hydrostatics) ──┐
Child B (FEM Chain)            ──┼──> Child D (Design Table + Round-Trip) ──> Child E (Skill Update)
Child C (STEP/INP for Gmsh)   ──┘
```

### Child A: Parametric Hull NURBS Generation + Hydrostatics
- **Repo:** digitalmodel
- **Complexity:** high
- **Blocked by:** none
- **Files:**
  1. `src/digitalmodel/visualization/design_tools/freecad_hull.py` (NEW)
  2. `src/digitalmodel/visualization/design_tools/hull_hydrostatics.py` (NEW)
  3. `tests/visualization/design_tools/test_freecad_hull.py` (NEW)
  4. `src/digitalmodel/visualization/design_tools/__init__.py` (update)
- **AC:** L=100m, B=20m, T=8m, Cb=0.7 → NURBS hull → hydrostatics within 2% of analytical
- **entry_reads:** `freecad_integration.py`, `profile_schema.py`, `hydrostatics.py`

### Child B: FEM Preprocessing Chain (FreeCAD → CalculiX)
- **Repo:** digitalmodel
- **Complexity:** high
- **Blocked by:** none
- **Files:**
  1. `src/digitalmodel/solvers/calculix/__init__.py` (NEW)
  2. `src/digitalmodel/solvers/calculix/inp_writer.py` (NEW)
  3. `src/digitalmodel/solvers/calculix/result_parser.py` (NEW)
  4. `src/digitalmodel/solvers/calculix/fem_chain.py` (NEW)
  5. `tests/solvers/calculix/test_fem_chain.py` (NEW)
- **AC:** Plate with hole → gmsh mesh → CalculiX → Kt within 5% of 3.0
- **Prerequisite:** `sudo apt install calculix-ccx`
- **entry_reads:** `gmsh_meshing/mesh_generator.py`, `freecad_integration.py`

### Child C: Gmsh STEP Import + CalculiX INP Export
- **Repo:** digitalmodel
- **Complexity:** medium
- **Blocked by:** none
- **Files:**
  1. `src/digitalmodel/solvers/gmsh_meshing/mesh_generator.py` (extend)
  2. `src/digitalmodel/solvers/gmsh_meshing/models.py` (extend)
  3. `tests/solvers/gmsh_meshing/test_gmsh_step_inp.py` (NEW)
- **AC:** STEP import via gmsh OCC kernel → volume mesh → INP export readable by CalculiX
- **entry_reads:** `gmsh_meshing/mesh_generator.py`, `gmsh_meshing/models.py`

### Child D: Design Table Studies + Round-Trip Validation
- **Repo:** digitalmodel
- **Complexity:** high
- **Blocked by:** [Child A, Child B, Child C]
- **Files:**
  1. `src/digitalmodel/visualization/design_tools/design_table.py` (NEW)
  2. `src/digitalmodel/visualization/design_tools/manifold_check.py` (NEW)
  3. `tests/visualization/design_tools/test_design_table.py` (NEW)
  4. `src/digitalmodel/visualization/design_tools/__init__.py` (update)
- **AC:** 3+ YAML parameter variations → batch generation → results comparison YAML; round-trip manifold check passes
- **entry_reads:** `parametric_hull.py` (pattern), outputs from A/B/C

### Child E: Freecad-Automation Skill Update
- **Repo:** workspace-hub
- **Complexity:** low
- **Blocked by:** [Child D]
- **Files:**
  1. `.claude/skills/engineering/cad/freecad-automation/SKILL.md` (update)
- **AC:** Documented workflows for hull gen, FEM chain, design tables, round-trip validation with code snippets

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| CalculiX apt install fails on Ubuntu 24.04 | Blocks Child B | Build from source or container fallback |
| FreeCAD 0.21.2 NURBS precision | Child A hydrostatics off by >2% | Sectional area integration fallback |
| Gmsh OCC kernel missing | Blocks Child C STEP import | Verify pip gmsh 4.15.1 includes OCC |
| FreeCAD thread safety | Child D parallelism fails | Sequential fallback, process isolation |
| Child B file count at limit (5) | Can't add files if needed | Keep fem_chain.py as thin orchestrator |

## Verification

After all children complete:
1. Run `test_freecad_hull.py` — hull generation + hydrostatics validation
2. Run `test_fem_chain.py` — plate with hole Kt ≈ 3.0 validation
3. Run `test_gmsh_step_inp.py` — STEP import + INP export
4. Run `test_design_table.py` — batch generation + manifold check
5. Full round-trip: FreeCAD hull → STEP → gmsh → STL → manifold pass
6. Cross-review the updated skill
