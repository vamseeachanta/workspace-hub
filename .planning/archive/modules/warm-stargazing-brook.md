# WRK-5082 Feature Plan — Parachute Frame Force Calculation

## Context

GT1R R35 parachute mounting frame — calculate structural loads during deployment at 200 and 250 MPH. Full engineering deliverable: 3D CAD, 2D drawings, 2D and 3D structural analysis, comparison, and engineering report.

## Existing Implementation (2D analytical — complete)

| Module | Purpose | Tests |
|---|---|---|
| `parachute_drag.py` | F = 0.5*rho*V^2*Cd*A*Cx | 22 |
| `frame_model.py` | 2D stick model + 4130 chromoly | 15 |
| `frame_solver.py` | 2D direct stiffness, 3 DOF/node | 22 |
| `member_check.py` | Von Mises, unity ratios, bolt/weld/pin | 16 |

## Existing Infrastructure (available in digitalmodel)

| Tool | Path | Status |
|---|---|---|
| FreeCAD agent | `.claude/agents/freecad/` | Available |
| CalculiX INP writer | `solvers/calculix/inp_writer.py` | Available (3D solids) |
| CalculiX result parser | `solvers/calculix/result_parser.py` | Available |
| CalculiX FEM chain | `solvers/calculix/fem_chain.py` | Available (plate geometry) |
| OrcaFlex | External — needs integration | TBD |

## Decomposition

| Child key | Child Title | Scope | blocked_by | orchestrator |
|---|---|---|---|---|
| 1 | 3D CAD geometry (FreeCAD) | Model frame from hand sketches and photos on dev-secondary | — | claude |
| 2 | 2D engineering drawing | Derive dimensioned 2D views from 3D CAD | 1 | claude |
| 3 | Chute drag force | Drag at 200 and 250 MPH (existing parachute_drag.py) | — | claude |
| 4 | 2D frame analysis | Extend frame_solver with under-hood frame (Page 2 geometry) | 1 | claude |
| 5 | 3D FEM analysis (CalculiX) | Beam FEM with stress distribution and deformation | 1 | claude |
| 6 | OrcaFlex frame analysis | Static frame model with applied drag force on licensed-win-1 | 1 | claude |
| 7 | 2D vs 3D comparison | Quantify simplification between direct stiffness and FEM | 4 | claude |
| 8 | Member and connection checks | Unity ratios and bolt weld pin checks with 3D results | 4 | claude |
| 9 | Pipeline and engineering report | End-to-end script and formatted calc report | 7 | claude |

## Dependency Graph

```
          1 (3D CAD)
         / | \
        2  5  6        3 (Drag)
        |  |  |         |
        |  |  |         4 (2D analysis)
        |  |  |         |
        |  7 ←+---------+
        |  |
        8 ←+
        |
        9 (Report — collects everything)
```

## Acceptance Criteria

1. 3D FreeCAD model matches hand sketches and photos
2. 2D drawings dimensioned and printable
3. Drag force calculated for 200 MPH and 250 MPH
4. 2D frame analysis: member forces, reactions, unity ratios
5. 3D FEM: stress contours, deformation, reaction forces
6. OrcaFlex: time-domain deployment load history
7. 2D vs 3D comparison: quantified error (%) per member
8. All unity ratios < 1.0 for assumed dimensions
9. Engineering report with all results, drawings, and conclusions

## Key Files

**Existing:** `digitalmodel/src/digitalmodel/structural/parachute/`
**Assets:** `.claude/work-queue/assets/WRK-5082/` (photos, sketches, PDF)
**FreeCAD agent:** `.claude/agents/freecad/`
**CalculiX:** `digitalmodel/src/digitalmodel/solvers/calculix/`
