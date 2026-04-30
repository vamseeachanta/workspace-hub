---
title: "Yaw Moment Rudder Sweep"
tags: [yaw, rudder, maneuvering, calculation-workflow]
sources:
  - pna-vol-iii-motions-controllability
  - usna-en400-principles-ship-performance-2020
  - practical-ship-hydrodynamics-bertram-2000
  - mctaggart-shipmo3d-maneuvering-2007
  - abs-vessel-maneuverability-guide-2017
added: 2026-04-30
last_updated: 2026-04-30
---

# Yaw Moment Rudder Sweep

This page is the knowledge anchor for workspace-hub issue #2564: a typical-ship input/schema and calculation surface for rudder-induced yaw moment across forward speed, rudder angle, density, dimensions, and lever arm.

Issue: <https://github.com/vamseeachanta/workspace-hub/issues/2564>

## Minimal bounded calculation

The first implementation target should be a transparent sweep:

```text
F_N = rudder normal force from existing maneuverability helper or equivalent validated formula
M_z = F_N * x_rudder_from_CG
```

Inputs to preserve in the YAML/data schema:

- forward ship speed or inflow velocity, `velocity_m_s`
- water density, `rho_kg_m3`
- rudder area, `rudder_area_m2`
- rudder span, `rudder_span_m`
- rudder angle, `rudder_angle_deg`
- stern/hull/propeller setting or explicit caveat flag
- yaw lever arm from CG to rudder force application point, `x_rudder_from_cg_m`
- convention metadata for rudder angle sign and yaw moment sign

## Why this is preliminary

PNA Vol. III, ABS, Bertram, and ShipMo3D all show that true maneuvering yaw response includes more than direct rudder normal force:

- sway velocity and drift angle
- yaw rate and yaw acceleration
- hull hydrodynamic derivatives
- rudder-hull interaction
- rudder-propeller interaction
- nonlinear effects in tight/steady turns
- environmental/current/wind yaw moments

Therefore #2564 should emit citation/provenance and caveats rather than imply full IMO/ABS maneuverability compliance.

## Sign convention requirements

Use [[maneuvering-coordinate-conventions]] to pin conventions before implementation:

- EN400 axes: `x` forward, `y` starboard, yaw about `z`.
- PNA rudder convention: positive stern-rudder deflection corresponds to a port-turn command.
- Tests must assert a named physical case, not just `M(+delta) = -M(-delta)`.

## Source-backed validation cases

Useful validation/acceptance checks before full maneuvering simulation:

1. **Quadratic speed scaling**: for fixed angle and dimensions, normal force should scale with `V^2` in the pre-stall simplified model.
2. **Odd angle symmetry near zero**: for a symmetric rudder and no bias terms, sign changes with rudder angle, but this must be combined with a named sign-convention test.
3. **Zero cases**: zero speed, zero density, zero area, or zero angle should produce zero or validation errors as appropriate.
4. **Operational limit warnings**: angles beyond ±35° should warn or be clearly outside the recommended pre-stall operating range.
5. **Citation sidecar**: outputs using standards/textbook-derived formulas must include provenance per workspace calc-citation contract.

## Upgrade path after #2564

- Add propeller-slipstream correction from Bertram / ShipMo3D.
- Add hull interaction amplification and center-of-effort shift from Bertram.
- Add ABS/PNA linear sway-yaw state-space model for coursekeeping/turning response.
- Add IMO/ABS maneuvering KPI validation: advance, transfer, tactical diameter, overshoot, stopping reach.
- Add environmental yaw moments from [[environmental-yaw-moment-coefficients]].

## Related pages

- [[rudder-force-modeling]]
- [[maneuvering-coordinate-conventions]]
- [[maneuvering-validation-metrics]]
- [[environmental-yaw-moment-coefficients]]
