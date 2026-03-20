# WRK-5082 Stage 4 Plan — Parachute Frame Force Calculation

## Context

WRK-5082 is a **Feature WRK** (complex, Route C) to calculate structural loads on a GT1R R35 parachute mounting frame during drag car parachute deployment at 200 and 250 MPH.

**Critical finding:** The entire analysis pipeline is already implemented and tested in `digitalmodel/src/digitalmodel/structural/parachute/` with **75 passing tests**. All 5 originally-planned decomposition children are covered by existing code.

## Existing Implementation (complete, tested)

| Module | Purpose | Tests |
|---|---|---|
| `parachute_drag.py` | F = 0.5*rho*V^2*Cd*A*Cx | 22 cases |
| `frame_model.py` | GT1R frame geometry + 4130 chromoly | 15 cases |
| `frame_solver.py` | 2D frame, 3 DOF/node (ux, uy, theta) | 22 cases |
| `member_check.py` | Von Mises, unity ratios, bolt/weld/pin | 16 cases |

## Gap Analysis

1. **No end-to-end pipeline** — modules work individually, no `pipeline.py`
2. **No formal results output** — no engineering summary (forces table, unity ratios, reactions)
3. **TBD items** — tube OD/wall (1.5" x 0.120"), chute model (12 ft, Cd=1.4), bolt sizes at B1

## Scripts-Over-LLM Audit

| Operation | Recurs? | Action |
|---|---|---|
| Full analysis pipeline | YES | Create `pipeline.py` |
| Results formatting | YES | Part of pipeline |

## Revised Feature Decomposition

| # | Child Title | Scope | blocked_by |
|---|---|---|---|
| 1 | Pipeline script | `pipeline.py` — chain drag->frame->checks | — |
| 2 | AC verification & results | Run both load cases, produce results YAML | 1 |
| 3 | Sensitivity & TBD resolution | Wall thickness sensitivity, document assumptions | 1 |

## Acceptance Criteria

1. `pipeline.py` runs for 200 MPH and 250 MPH without error
2. Output: drag force, member forces, reactions at C3, Von Mises, unity ratios
3. All unity ratios < 1.0 for 1.5" OD x 0.120" wall
4. Bolt, weld, pin connection checks included
5. Existing 75 tests still pass

## Pseudocode — `pipeline.py`

```python
def run_analysis(speed_mph, chute_diameter_ft, cd, cx):
    drag = calculate_drag_force(speed_mph, chute_diameter_ft, cd, cx, rho)
    frame = build_gt1r_frame(bar_od=1.5, bar_wall=0.120)
    result = solve_frame(frame.nodes, frame.members, frame.fixed_nodes,
                         {frame.load_node: {"fy": -drag.force_lbs}},
                         frame.material["E_psi"])
    checks = check_all_members(result.member_forces,
                               tube_section_properties(1.5, 0.120),
                               frame.material)
    connections = check_connections(result, frame)
    return AnalysisResults(drag, result, checks, connections)
```

## Test Plan

| # | What | Type | Expected |
|---|---|---|---|
| 1 | Pipeline 200 MPH | Happy | All fields populated |
| 2 | Pipeline 250 MPH | Happy | Higher forces |
| 3 | All UR < 1.0 at 200 MPH | Happy | Pass |
| 4 | Reactions = applied force | Equilibrium | Within 0.1% |
| 5 | Negative speed | Error | ValueError |
| 6 | Zero wall thickness | Edge | ValueError |
| 7 | Halved wall -> higher UR | Sensitivity | UR increases |

## Key Files

**Existing:** `digitalmodel/src/digitalmodel/structural/parachute/{parachute_drag,frame_model,frame_solver,member_check}.py`

**To create:** `pipeline.py`, `test_pipeline.py`

## Verification

```bash
cd digitalmodel && PYTHONPATH=src uv run python -m pytest tests/structural/parachute/ -v
```
