# WRK-1251 Feature Plan: FreeCAD Deep Parametric Engineering

## Context

WRK-1251 aims to enable production-grade FreeCAD automation for hull generation, FEM analysis, design table studies, and round-trip validation. **Most of the code already exists** — this plan focuses on validation, gap-filling, and integration.

### What Already Exists

| Component | File | Status |
|-----------|------|--------|
| Hull NURBS generator | `digitalmodel/.../design_tools/freecad_hull.py` (176 lines) | Built |
| Hull hydrostatics | `digitalmodel/.../design_tools/hull_hydrostatics.py` (162 lines) | Built |
| Design table (hydro) | `digitalmodel/.../design_tools/design_table.py` (246 lines) | Built |
| Manifold checker | `digitalmodel/.../design_tools/manifold_check.py` (190 lines) | Built |
| Gmsh meshing + INP export | `digitalmodel/.../solvers/gmsh_meshing/mesh_generator.py` (294 lines) | Built |
| FEM chain (CalculiX) | `digitalmodel/.../solvers/calculix/fem_chain.py` (326 lines) | Built |
| INP writer (BCs/materials) | `digitalmodel/.../solvers/calculix/inp_writer.py` (199 lines) | Built |
| Result parser (.frd/.dat) | `digitalmodel/.../solvers/calculix/result_parser.py` (207 lines) | Built |
| FEM tests (skip if no ccx) | `digitalmodel/tests/solvers/calculix/test_fem_chain.py` (499 lines) | Built |

### True Remaining Gaps

1. **CalculiX (`ccx`) not installed** on dev-secondary — hard blocker for FEM integration tests
2. **Hull hydrostatics not validated** against analytical (2% AC tolerance)
3. **Design table lacks FEM mode** — only does hull hydrostatics, not structural FEM
4. **No end-to-end round-trip test** — individual pieces untested as a chain
5. **Skill documentation** — freecad-automation skill needs deep workflow sections

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | CalculiX installation and FEM chain validation | Install ccx on dev-secondary, run existing FEM tests, verify plate-with-hole Kt within 5% of 3.0 | — | claude | |
| child-b | Hull hydrostatics analytical validation | Validate HullHydrostatics against box-barge analytical (V, Awp, KB, BM) within 2% tolerance | — | claude | |
| child-c | Design table FEM extension | Add batch FEM mode to DesignTable — vary plate/hole params, run FEMChain, export comparison YAML | child-a | claude | |
| child-d | Round-trip pipeline integration test | Chain FreeCAD hull → STEP → gmsh mesh → STL → ManifoldChecker and verify closed surface | child-b | claude | |
| child-e | Freecad-automation skill deep workflow update | Add parametric hull, FEM chain, and design table workflow sections to freecad-automation skill | child-b, child-c, child-d | claude | |

### Child: child-a

**Files/skills needed (entry_reads):**
- `digitalmodel/src/digitalmodel/solvers/calculix/fem_chain.py`
- `digitalmodel/tests/solvers/calculix/test_fem_chain.py`
- `digitalmodel/src/digitalmodel/solvers/calculix/inp_writer.py`
- `digitalmodel/src/digitalmodel/solvers/calculix/result_parser.py`

**Acceptance Criteria:**
- [ ] `ccx` binary installed and callable on dev-secondary
- [ ] `test_fem_chain.py` integration tests pass (previously skipped due to no ccx)
- [ ] Plate-with-hole Kt within 5% of 3.0 (d/W < 0.3)

**Route:** A (install + run existing tests)
**Repo:** digitalmodel (test validation only, no new source files)

### Child: child-b

**Files/skills needed (entry_reads):**
- `digitalmodel/src/digitalmodel/visualization/design_tools/hull_hydrostatics.py`
- `digitalmodel/src/digitalmodel/visualization/design_tools/freecad_hull.py`
- `digitalmodel/src/digitalmodel/hydrodynamics/hull_library/profile_schema.py`

**Acceptance Criteria:**
- [ ] Box-barge test: V = L×B×T within 2%, Awp = L×B within 2%
- [ ] KB = T/2 and BM = B²/(12T) within 2% for wall-sided vessel
- [ ] Cb=0.7 hull profile: displacement = ρ×L×B×T×Cb within 2%
- [ ] All tests in new `test_hull_hydrostatics_validation.py` pass

**Route:** B (validation + possible numerical fixes, 1 repo)
**Repo:** digitalmodel

### Child: child-c

**Files/skills needed (entry_reads):**
- `digitalmodel/src/digitalmodel/visualization/design_tools/design_table.py`
- `digitalmodel/src/digitalmodel/solvers/calculix/fem_chain.py`

**Acceptance Criteria:**
- [ ] `DesignTable` supports FEM parameter variations (plate thickness, hole diameter, material E)
- [ ] 3+ parameter variations → batch FEMChain → results comparison YAML
- [ ] Test validates monotonic Kt variation with hole/plate width ratio

**Route:** B (extend existing module, 1 repo)
**Repo:** digitalmodel

### Child: child-d

**Files/skills needed (entry_reads):**
- `digitalmodel/src/digitalmodel/visualization/design_tools/freecad_hull.py`
- `digitalmodel/src/digitalmodel/solvers/gmsh_meshing/mesh_generator.py`
- `digitalmodel/src/digitalmodel/visualization/design_tools/manifold_check.py`

**Acceptance Criteria:**
- [ ] Integration test: hull profile → FreeCAD STEP → gmsh volume mesh → STL export
- [ ] ManifoldChecker reports `pass: true` on the exported geometry
- [ ] All operations headless via freecadcmd (skip if FreeCAD unavailable)

**Route:** B (integration test, chains existing modules, 1 repo)
**Repo:** digitalmodel

### Child: child-e

**Files/skills needed (entry_reads):**
- `.claude/skills/engineering/cad/freecad-automation/SKILL.md`
- All source files from children a-d

**Acceptance Criteria:**
- [ ] Parametric hull workflow section added to freecad-automation skill
- [ ] FEM chain workflow section with CalculiX pipeline documented
- [ ] Design table studies section with examples

**Route:** A (documentation only)
**Repo:** workspace-hub

## Dependency Graph

```
child-a (CalculiX install)  ─────────┐
                                      ├──> child-c (Design table FEM)
                                      │              │
child-b (Hydrostatics validation) ────┤              ├──> child-e (Skill update)
                                      │              │
                                      ├──> child-d (Round-trip pipeline)
                                      │              │
                                      └──────────────┘
```

Children a and b execute in parallel. c needs a. d needs b. e needs b+c+d.

## Verification

After all children complete:
1. `ccx --version` returns valid CalculiX version
2. `PYTHONPATH=src uv run python -m pytest tests/solvers/calculix/` — all pass (no skips)
3. `PYTHONPATH=src uv run python -m pytest tests/visualization/design_tools/test_hull_hydrostatics_validation.py` — all pass
4. `PYTHONPATH=src uv run python -m pytest tests/integration/test_freecad_roundtrip.py` — pass or skip (if no FreeCAD)
5. Freecad-automation skill has 3+ new workflow sub-skill sections
