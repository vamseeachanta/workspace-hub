---
title: B1528 SIROCCO Rudder Yaw-Moment Inputs
tags: [concept, rudder, yaw-moment, input-file, time-trace, benchmark]
added: 2026-05-01
last_updated: 2026-05-01
sources:
  - github://vamseeachanta/acma-projects/B1528/excel_to_py/Rudder Force & Yaw Moments.xlsx
  - github://vamseeachanta/acma-projects/B1528/ref/SIROCCO breakaway notes.docx
domain: acma-projects
cross_links:
  - ../entities/b1528-sirocco-breakaway.md
  - ../sources/b1528-rudder-force-yaw-moments-workbook.md
  - ../sources/b1528-sirocco-breakaway-notes.md
---

# B1528 SIROCCO Rudder Yaw-Moment Inputs

This page captures the project-specific input evidence needed before implementing a SIROCCO/Sorrocco yaw-moment input file, static sweep charts, and first-order time trace.

## Input quantities ready for YAML

| Input | Value | Units | Source |
|---|---:|---|---|
| Vessel/project name | SIROCCO / B1528 | — | workbook titles and breakaway notes |
| LBP | 225.5 | m | `Rudder Area and Ctr!D7` |
| Breadth molded | 32.26 | m | `Rudder Area and Ctr!D8` |
| Design draft | 12.2 | m | `Rudder Area and Ctr!D10` |
| Rudder area | 44.9395631937 | m² | `Rudder Area and Ctr!C25` |
| Rudder center aft of AP | -1.0520261379 | m | `Rudder Area and Ctr!C26` |
| Yaw lever in legacy workbook | 135.3 | m | `0.6 * LBP`, `Barrass!B29` |
| Rudder constant | 600 | — | `Barrass!C17` |
| Port prop rotation factor | 1.065 | — | `Barrass!C19`, `Barrass-chk!C30` |
| Starboard prop rotation factor | 0.935 | — | `Barrass` sheet note (`1.065` port / `0.935` stbd); converted script corroborates but is not canonical |
| Requested forward speed | 2.5 | kn | user request + workbook note |
| Requested rudder angles | +1, -1 | deg | user request |

## Required calculation/report slices

1. Static yaw-moment chart review over varying forward speeds and rudder attack angles.
2. Dedicated `+1 deg` and `-1 deg` operating-point calculation at `2.5 kn`.
3. Interactive charts that show yaw moment vs rudder angle, yaw moment vs speed, and force/moment companions.
4. Time-trace method where yaw rate changes the rudder-local inflow angle, changing effective rudder attack angle.
5. Benchmark comparison against structured SIROCCO turning/track evidence from breakaway notes.

## Recommended numerical method boundary

For a bounded first implementation, use a constant-speed first-order Nomoto trajectory model with rudder-local inflow correction:

- State: heading `psi`, yaw rate `r`, earth-fixed `x/y`.
- Local lateral inflow at rudder: `v_R = x_R * r`.
- Rudder inflow angle: `beta_R = atan2(-x_R * r, U)`.
- Effective rudder angle: `alpha_R = delta_cmd - beta_R`.
- Local rudder speed: `U_R = sqrt(U^2 + v_R^2)`.
- Nomoto yaw ODE: `r_dot = (K * alpha_R - r) / T` with user/calibrated `K` and `T`.
- Kinematics: `psi_dot = r`, `x_dot = U cos(psi)`, `y_dot = U sin(psi)`.

This preserves the intended feedback — yaw changes rudder attack angle relative to fluid speed — without claiming a full MMG or incident-reconstruction model.

## Critical caveats

- The B1528 incident includes tugs, anchors, current, bank effects, and propulsion; a simple yaw-moment/Nomoto model is a preliminary engineering calculation only.
- The legacy workbook yaw moment uses normal force in metric tons times a 60% LBP lever, despite surrounding text mentioning transverse force. Downstream code/report must state which convention is used.
- Turning/track benchmark evidence must be extracted into a structured table before numerical comparison.

## Related pages

- [B1528 SIROCCO Breakaway](../entities/b1528-sirocco-breakaway.md)
- [B1528 rudder force/yaw moments workbook](../sources/b1528-rudder-force-yaw-moments-workbook.md)
- [B1528 SIROCCO breakaway notes](../sources/b1528-sirocco-breakaway-notes.md)
