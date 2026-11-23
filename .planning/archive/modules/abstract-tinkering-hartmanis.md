# WRK-5082: Parachute Frame Force Calculation (Feature Plan)

## Context

A client has a GT1R Nissan GT-R R35 drag car with a bolt-on parachute kit (4130 chromoly steel frame). They need structural verification of the parachute mounting frame under deployment loads at 200 MPH and 250 MPH. Hand sketches with dimensions, photos, and reference videos have been provided. The work decomposes naturally into 5 sequential engineering tasks — from geometry capture through final acceptability checks.

## Existing Infrastructure (digitalmodel)

| Component | Path | Reuse |
|-----------|------|-------|
| Von Mises stress calculator | `structural/stress/vm_stress.py` | 85% — PipeStressAnalyzer handles axial+bending on tubes |
| BeamElement (Euler-Bernoulli) | `base_solvers/structural/elements/beam_element.py` | 95% — 2D frame, 4 DOF/element, axial+bending |
| StructuralSolver base | `base_solvers/structural/base.py` | 40% — needs beam element integration |
| Material properties | `base_solvers/structural/config.py` + `vm_stress.py` | 90% — add 4130 chromoly |
| FEA/CAD automation | `solvers/fea_model/`, `solvers/blender_automation/`, `.claude/agents/freecad/` | Available |
| Drag/aerodynamics | — | 0% — **build new** |

## Scripts to Create

| Script | Inputs | Outputs | Created in |
|--------|--------|---------|------------|
| `parachute_drag.py` | speed, air density, chute diameter, Cd | drag force (lbs/N) | Child 3 |
| `frame_solver.py` | node coords, elements, BCs, loads | member forces, reactions | Child 4 |
| `member_check.py` | member forces, section props, material | unity ratios, pass/fail | Child 5 |

## Decomposition

| Child key | Title | Scope (one sentence) | Depends on | Agent | wrk_ref |
|-----------|-------|----------------------|------------|-------|---------|
| child-a | CAD drawing — sketch to structural model | Convert hand sketches and photos into a dimensioned stick/line model with node coordinates and member connectivity | — | claude | |
| child-b | Dimensions material properties and connections | Tabulate tube OD/wall thickness, 4130 chromoly properties (Fy=63 ksi, Fu=97 ksi, E=29.7 Msi), and connection details (weld sizes, bolt grades, pin diameters) | child-a | claude | |
| child-c | Chute drag force calculation | Calculate parachute drag force at 200 and 250 MPH using F=0.5*rho*V^2*A*Cd with Stroud chute parameters | — | claude | |
| child-d | Load distribution through frame | Distribute chute drag through structural members using 2D frame analysis — resolve axial/shear/bending at each joint and reactions at body mounts | child-a, child-b, child-c | claude | |
| child-e | Member and connection acceptability checks | Von Mises and ASME combined stress checks, unity ratios for each member, bolt/weld adequacy at all connections | child-d | claude | |

### Child: child-a — CAD Drawing

**Scope**: Convert hand-sketched geometry (hand-sketches-structural-geometry.pdf + annotated-sketch-force-diagram.jpeg + photos) into a dimensioned structural model. Output is a node-coordinate table and member-connectivity list suitable for frame analysis.

**Entry reads**: `assets/WRK-5082/` (all photos + PDF)

**Acceptance criteria**:
- Node coordinates (x, y) for all joints in consistent units (inches)
- Member connectivity table (node-i, node-j, member-type)
- Connection types mapped (C0–C3, B1, coupler pin)
- Boundary conditions identified at each support
- Geometry validated against hand sketch dimensions (6+12+12+6=36", 7.25" offset)

### Child: child-b — Dimensions, Material Properties, Connections

**Scope**: Compile all section properties and material data needed for analysis. 4130 chromoly steel per ASTM A519 (normalized condition). Cross-section geometry from manual measurements or best estimates from photos.

**Entry reads**: child-a output (node/member table), `vm_stress.py` MaterialProperties

**Acceptance criteria**:
- 4130 chromoly properties sourced (Fy, Fu, E, nu, density) with reference
- Tube OD and wall thickness per member (measured or estimated with stated basis)
- Section properties computed (A, I, S, r) per member
- Connection capacity data: weld throat sizes, bolt grade/diameter, pin shear area
- All data in YAML format consumable by frame solver

### Child: child-c — Chute Drag Force

**Scope**: Calculate parachute opening shock force at 200 MPH and 250 MPH. Use standard aerodynamic drag equation with appropriate Cd for hemispherical/ribbon chute. Account for opening shock factor (Cx ≈ 1.2–1.8 for sudden deployment).

**Entry reads**: WRK-5082 design basis (chute diameter, vehicle weight, Stroud data)

**Acceptance criteria**:
- Drag force at 200 MPH with Cd and opening shock factor stated
- Drag force at 250 MPH with same
- Air density assumption stated (sea level standard = 0.002378 slug/ft³)
- Sensitivity to Cd variation (±20%) reported
- Force in both lbs and N
- Test: hand-calc verification against F = 0.5 * rho * V² * Cd * A * Cx

### Child: child-d — Load Distribution Through Frame

**Scope**: Apply chute drag force to the frame model and solve for member forces using 2D frame analysis. Extend existing BeamElement/StructuralSolver or build a lightweight frame solver.

**Entry reads**: child-a (geometry), child-b (properties), child-c (loads), `beam_element.py`, `base.py`

**Acceptance criteria**:
- Reaction forces at each body mount point (C3 rigid, B1 bolted)
- Axial force, shear force, and bending moment per member
- Load path narrative: which members in tension/compression/bending
- Equilibrium check: sum of reactions = applied load (within 0.1%)
- Both load cases (200 MPH, 250 MPH)

### Child: child-e — Member and Connection Acceptability

**Scope**: Stress checks on each member and connection. Use von Mises yield criterion and ASME combined stress. Report unity ratios (demand/capacity).

**Entry reads**: child-d (member forces), child-b (properties), `vm_stress.py`

**Acceptance criteria**:
- Von Mises stress per member vs 0.6*Fy allowable (ASD basis)
- ASME combined stress check per member
- Unity ratio table (demand/capacity) — all must be ≤ 1.0 to pass
- Bolt shear/bearing/tensile check at each connection
- Weld throat stress check at C0, C2, C3
- Pin shear check at coupler
- Critical member identified (highest unity ratio)
- Pass/fail verdict with recommendations if any member fails

## Verification

```bash
# After all children complete:
# 1. Equilibrium check
uv run --no-project python -c "
# sum of reactions == applied drag force (both cases)
"

# 2. Unit tests pass
cd digitalmodel && PYTHONPATH=src uv run python -m pytest tests/structural/ -v

# 3. Unity ratios all ≤ 1.0
# Check output of member_check.py
```
