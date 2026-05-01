---
title: "ABS Guide for Vessel Maneuverability"
tags: [abs, maneuvering, yaw, validation]
sources:
  - "/mnt/ace/acma-codes/ABS Rules/Vessel Maneuverability/Vessel_Maneuverability_Guide_e-Feb17.pdf"
added: 2026-04-30
last_updated: 2026-04-30
---

# ABS Guide for Vessel Maneuverability

Raw path: `/mnt/ace/acma-codes/ABS Rules/Vessel Maneuverability/Vessel_Maneuverability_Guide_e-Feb17.pdf`

## Relevance

ABS Appendix 3 is the strongest local source for an implementation-ready reduced maneuvering model with surge/sway/yaw equations and rudder contributions.

## Extracted model content

3-DOF ship-fixed equations:

```text
m(u_dot - v r - x_cg r^2) = X + X_Rd
m(v_dot + u r + x_cg r_dot) = Y + Y_Rd
I_z r_dot + m x_cg(v_dot + u r) = N + N_Rd
```

Linearized rudder-force closure:

```text
X_Rd = 0
Y_Rd = Y_delta * delta_R
N_Rd = N_delta * delta_R
```

ABS then rearranges the sway-yaw equations into state-space/Cauchy form `X_dot = A X + H`.

Raw locators: Appendix 3 §2.1-2.7, PDF pp.59-65.

## Validation/rating content

ABS reuses IMO pass/fail maneuverability concepts and adds ratings:

```text
Rt = 0.25 * (Rtd + Rt_alpha + Rti + Rts)
```

Raw locators: Section 1-2, PDF pp.3 and 9-18.

## Use in #2564

Use ABS as a future upgrade path and context source. Do not claim ABS compliance for a direct rudder-normal-force yaw-moment sweep.

Related: [[yaw-moment-rudder-sweep]], [[maneuvering-validation-metrics]].
