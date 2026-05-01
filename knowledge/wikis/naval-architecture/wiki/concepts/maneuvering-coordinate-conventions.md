---
title: "Maneuvering Coordinate Conventions"
tags: [maneuvering, coordinates, yaw, sign-convention]
sources:
  - usna-en400-principles-ship-performance-2020
  - pna-vol-iii-motions-controllability
added: 2026-04-30
last_updated: 2026-04-30
---

# Maneuvering Coordinate Conventions

This page captures the coordinate and sign conventions needed before implementing [[rudder-force-modeling]] and [[yaw-moment-rudder-sweep]].

## Ship axes and motions

USNA EN400 §1.8 is the cleanest local reference for the default ship axes:

- `x`: longitudinal axis; positive forward of amidships.
- `y`: transverse/athwartship axis; positive starboard, negative port.
- `z`: vertical axis, referenced to keel/baseline.
- Motions:
  - surge: translation in `x`
  - sway: translation in `y`
  - heave: translation in `z`
  - roll: rotation about `x`
  - pitch: rotation about `y`
  - yaw: rotation about `z`

Raw locator: `/mnt/ace/O&G-Standards/SNAME/textbooks/USNA-EN400-Principles-Ship-Performance-2020.pdf`, PDF p.35 / printed p.1-25.

## Maneuvering variables

PNA Vol. III frames horizontal-plane maneuvering in surge, sway, and yaw:

- `u`: forward/surge velocity.
- `v`: sway velocity.
- `ψ`: heading / yaw angle of ship longitudinal axis relative to earth-fixed axes.
- `r = ψ_dot`: yaw rate.
- `β`: drift/leeway angle between heading and actual course/velocity-vector tangent.

Raw locator: `/mnt/ace/O&G-Standards/SNAME/textbooks/Principles-of-Naval-Architecture-SecondRevision-Vol3-Motions-Controllability.pdf`, PDF pp.148-149 / printed pp.193-194.

## Rudder sign convention from PNA

PNA Vol. III explicitly states that, for stern rudders, positive rudder deflection corresponds to a turn to port:

> `δR` = rudder-deflection angle; positive deflection corresponds to a turn to port for rudder(s) located at stern.

Raw locator: PNA Vol. III, PDF p.154 / printed p.199, near Eq. (12).

## Implementation implication for #2564

The first yaw-moment sweep must make its convention executable and non-tautological:

- Define `rudder_angle_deg > 0` as a port-turn command unless the implementation deliberately overrides PNA.
- Define `lever_arm_x_m` sign relative to CG and document whether positive aft or forward is used in the implementation API.
- For a stern rudder located aft of CG, a positive port-turn command should create a yaw moment sign consistent with the chosen right-handed `z` convention.
- Tests must pin at least one named case with expected sign, not only check anti-symmetry.

## Related pages

- [[yaw-moment-rudder-sweep]]
- [[rudder-force-modeling]]
- [[maneuvering-validation-metrics]]
