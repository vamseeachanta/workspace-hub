# WRK-1364: 3D FEM Analysis (CalculiX) — Implementation Plan

## Context

The GT1R R35 parachute mounting frame needs 3D FEM analysis to capture out-of-plane bending, torsion, and stress concentrations that the 2D direct stiffness model cannot. All three blockers are done:
- **WRK-1360**: 15-node, 16-member 3D geometry (`frame_geometry_3d.py`)
- **WRK-1362**: Drag forces — 24,289 lbs (200 single), 37,952 lbs (250 single), 52,712 lbs (250 dual)
- **WRK-1341**: CalculiX INP writer with B31/B32 beam sections

**Decisions confirmed**: B31 straight + B32 curved, B1 fully fixed, all 3 load cases, post-processing includes load distribution and strains across members.

## Step 1: Frame-to-FEM Bridge Module

**File**: `digitalmodel/src/digitalmodel/structural/parachute/fem_bridge.py`

Build a bridge that converts `FrameGeometry3D` → CalculiX INP using the existing `INPWriter`:

1. Convert 15 `Node3D` objects → numpy node array (inches)
2. Convert 16 `Member3D` objects → element connectivity
   - Straight members → `"Line 2"` (B31)
   - Bend members (`is_bend=True`, 4 total) → `"Line 3"` (B32) with mid-node interpolation
3. Define beam section: PIPE type with `(OD/2, wall)` = `(0.875, 0.120)`
4. Define material: 4130 chromoly — E=29.7e6 psi, nu=0.29
5. Apply boundary conditions:
   - C3 nodes (7, 10): fix DOFs 1-6
   - B1 nodes (12, 14): fix DOFs 1-6 (per decision: fully fixed)
6. Apply concentrated loads at N1 (parachute bracket, node_id=1):
   - Direction: -Y (rearward, opposing vehicle forward motion)
   - Magnitude: drag force from each load case
7. Write one INP file per load case (3 total)

**Key reuse**:
- `frame_geometry_3d.build_gt1r_frame_3d()` — geometry
- `INPWriter` — all INP generation
- `chute_assessment.assess_all_load_cases()` — load values

## Step 2: FEM Runner Script

**File**: `digitalmodel/src/digitalmodel/structural/parachute/run_fem_3d.py`

Orchestration script:
1. Build geometry via `build_gt1r_frame_3d()`
2. Get load cases via `assess_all_load_cases()`
3. For each load case, call `fem_bridge` to generate INP
4. Run `ccx <job_name>` via subprocess
5. Parse results via `CalculiXResultParser`
6. Extract per load case:
   - Max von Mises stress + location (node, member)
   - Utilisation ratio = max_stress / Fy (63,000 psi)
   - Displacement at N1 (chute attachment)
   - Reaction forces at C3 and B1 nodes
   - **Member-level load distribution** (axial force, shear, bending moment per member)
   - **Strains** at all nodes (from stress/E for elastic range)
7. Export results to YAML for WRK-1366/1367

## Step 3: Post-Processing — Load Distribution & Strains

**Enhancement to `result_parser.py`** (extend, don't rewrite):

1. Add `get_strains()` method — compute ε = σ/E for each stress component at each node
2. Add `get_element_forces()` method — extract section forces (N, Vy, Vz, Mx, My, Mz) from `.dat` file
   - CalculiX outputs these via `*SECTION PRINT` or `*EL PRINT, ELSET=<set>` with `SF` (section forces)
3. Map element forces back to member labels using the geometry bridge

**INP additions for load distribution output**:
- Add `*EL FILE` with `S, E` (stress + strain output to .frd)
- Add `*SECTION PRINT` for beam section forces per element set
- Add `*NODE PRINT, NSET=<bc_nodes>` for reaction forces in .dat

## Step 4: Results Summary Module

**File**: `digitalmodel/src/digitalmodel/structural/parachute/fem_results_3d.py`

Structured results dataclass:
- Per-load-case summary (stress, displacement, utilisation)
- Per-member load distribution table (axial, shear, moment)
- Per-node strain table
- Reaction force table at all BC nodes
- YAML export function for WRK-1366/1367

## Step 5: Tests (TDD)

**File**: `digitalmodel/tests/structural/parachute/test_fem_3d.py`

1. `test_fem_bridge_node_count()` — 15 nodes in INP
2. `test_fem_bridge_element_count()` — 16 elements (12 B31 + 4 B32)
3. `test_fem_bridge_bc_nodes()` — DOFs 1-6 fixed at nodes 7,10,12,14
4. `test_fem_bridge_load_direction()` — CLOAD at node 1 in -Y
5. `test_fem_bridge_beam_section()` — PIPE section with correct dims
6. `test_fem_bridge_generates_valid_inp()` — write + validate structure
7. `test_ccx_runs_without_error()` — integration test (requires ccx)
8. `test_results_stress_positive()` — max von Mises > 0
9. `test_results_displacement_at_load_point()` — N1 displacement > 0
10. `test_results_reaction_equilibrium()` — sum(reactions) ≈ applied load
11. `test_member_load_distribution()` — all members have force data
12. `test_strain_values()` — strains computed for all nodes

## Step 6: Calculation Report (YAML + HTML)

**File**: `examples/reporting/fem-3d-beam-analysis-wrk-1364.yaml`

Following the `calculation-report` skill (6-phase methodology):

| Section | Content |
|---------|---------|
| metadata | CALC-WRK-1364, rev 1, draft |
| scope | 3D FEM beam analysis objective, inclusions/exclusions |
| design_basis | Euler-Bernoulli/Timoshenko beam theory, CalculiX B31/B32 |
| inputs | Geometry (15 nodes, 16 members), material (4130), loads (3 cases) |
| methodology | FEM formulation, element selection rationale, BC justification |
| calculations | Step-by-step per load case with intermediate results |
| outputs | Max stress, utilisation, displacement, reactions per case |
| sensitivity | Not required (parametric study in WRK-1367) |
| validation | Cantilever benchmark (WRK-1341), equilibrium check |
| charts | Bar chart: member load distribution, stress contour summary |
| data_tables | Member forces table, reaction forces table, strain table |
| references | CalculiX manual, AISI 4130 data sheet, WRK-1360/1362/1341 |

Generate HTML report via:
```bash
uv run --no-project python scripts/reporting/generate-calc-report.py examples/reporting/fem-3d-beam-analysis-wrk-1364.yaml
```

## Critical Files

| File | Action |
|------|--------|
| `digitalmodel/src/digitalmodel/structural/parachute/fem_bridge.py` | Create |
| `digitalmodel/src/digitalmodel/structural/parachute/run_fem_3d.py` | Create |
| `digitalmodel/src/digitalmodel/structural/parachute/fem_results_3d.py` | Create |
| `digitalmodel/src/digitalmodel/solvers/calculix/result_parser.py` | Extend (strains, element forces) |
| `digitalmodel/src/digitalmodel/solvers/calculix/inp_writer.py` | Extend (SECTION PRINT, NODE PRINT) |
| `digitalmodel/tests/structural/parachute/test_fem_3d.py` | Create |
| `examples/reporting/fem-3d-beam-analysis-wrk-1364.yaml` | Create |
| `digitalmodel/src/digitalmodel/structural/parachute/frame_geometry_3d.py` | Read only |
| `digitalmodel/src/digitalmodel/structural/parachute/chute_assessment.py` | Read only |

## Verification

1. `uv run pytest tests/structural/parachute/test_fem_3d.py -v` — all tests pass
2. `uv run pytest tests/solvers/calculix/ -v` — no regressions
3. `ccx` runs to completion for all 3 load cases (check .sta files for convergence)
4. Equilibrium check: sum of reaction forces = applied load (within 0.1%)
5. Sanity: utilisation ratio < 1.0 for at least the 200 MPH case
6. YAML schema validation before report generation
7. HTML report renders correctly with charts
