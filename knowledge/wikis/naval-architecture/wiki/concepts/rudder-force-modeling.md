---
title: "Rudder Force Modeling"
tags: [maneuvering, rudder, hydrodynamics, yaw]
sources:
  - pna-vol-iii-motions-controllability
  - usna-en400-principles-ship-performance-2020
  - practical-ship-hydrodynamics-bertram-2000
  - mctaggart-shipmo3d-maneuvering-2007
added: 2026-04-30
last_updated: 2026-04-30
---

# Rudder Force Modeling

This page collects local raw-reference guidance for rudder force estimates used by [[yaw-moment-rudder-sweep]]. It deliberately separates the **bounded preliminary rudder-normal-force model** from higher-fidelity hull-propeller-rudder maneuvering models.

## Geometry vocabulary

PNA Vol. III §14.1 defines standard control-surface geometry terms:

- root chord
- tip chord
- mean chord
- mean span
- geometric aspect ratio
- taper ratio
- profile area

Raw locator: PNA Vol. III, PDF p.246 / printed p.291.

USNA EN400 §9.3.1 adds practical constraints:

- Rudder chord is limited by propeller/rudder clearance and stern geometry.
- Rudder span is limited by draft and grounding/baseline constraints.
- Typical span is approximately propeller diameter.

Raw locator: USNA EN400, PDF p.332 / printed p.9-5.

## Force and coefficient definitions

Bertram §5.4.2 gives common rudder coefficient definitions using dynamic pressure `q = 0.5 rho V^2`, rudder area `A_R`, mean chord `c_m`, and aspect ratio `Λ = b^2/A_R`:

- `C_L = L / (q A_R)`
- `C_D = D / (q A_R)`
- `C_QN = Q_N / (q A_R c_m)`
- `C_QR = Q_R / (q A_R c_m)`

Raw locator: `/mnt/ace/O&G-Standards/SNAME/hydrostatics-stability/Practical-Ship-Hydrodynamics-Bertram-2000.pdf`, §5.4.2, printed pp.181-185.

## Preliminary force model scope

A bounded first-pass yaw calculation may use a rudder normal force `F_N` and a CG lever arm:

```text
M_z = F_N * x_rudder_from_CG
```

This is appropriate for #2564 as a sweep/parametric input workflow, not a complete maneuvering simulator. PNA and ABS both show that full maneuvering also includes hull sway/yaw derivatives, drift angle, and added hydrodynamic effects.

## Dependence on speed, angle, and area

USNA EN400 §9.2.2 states that ship response depends on:

- rudder dimensions
- rudder angle
- ship speed

USNA also gives a rudder-area-ratio context:

```text
Rudder area ratio = Rudder area / (LPP * T)
```

with cited values from roughly `0.017` for cargo ships to `0.025` for destroyers.

Raw locator: USNA EN400, PDF p.330 / printed p.9-3.

## Angle limits and stall

USNA EN400 and PNA Vol. III both warn that rudder lift is pre-stall only:

- typical rudder range: about `±35 deg`
- full stall shown around `45 deg`
- after stall, lift drops and drag rises quickly
- PNA defines stall as an abrupt discontinuity in lift versus angle-of-attack curve

Raw locators:

- USNA EN400, PDF pp.334-336 / printed pp.9-7 to 9-9.
- PNA Vol. III, PDF p.248 / printed p.293.

## Aspect ratio and effective angle correction

Bertram gives a useful effective rudder-angle correction for comparing aspect ratios:

```text
delta_eff = (2.2 * Lambda / (Lambda + 2.4)) * delta
```

Bertram also notes typical maximum lift coefficient for ship rudders around `1.2 < C_L,max < 1.4`, nearly independent of aspect ratio.

Raw locator: Bertram §5.4.2, printed p.185.

## Propeller interaction caveat

Bertram §5.4.4 and ShipMo3D both show that a rudder behind a propeller can see much larger force due to slipstream.

Bertram simple correction:

```text
Delta L = T * (1 + 1/sqrt(1 + C_Th)) * sin(delta)
Delta D = T * (1 + 1/sqrt(1 + C_Th)) * (1 - cos(delta))
C_Th = T / (0.5 * rho * V_A^2 * A_P) = 8 K_T / (pi J^2)
```

ShipMo3D uses a similar form with an interaction coefficient `C_rudder-prop in [0, 1]`; McTaggart identifies this coefficient as a major uncertainty.

Raw locators:

- Bertram §5.4.4, printed pp.190-193.
- `/mnt/ace/digitalmodel/docs/ship-design/literature/maneuvering_ship.pdf`, §9, printed pp.16-17.

## Hull interaction caveat

Bertram §5.4.5 describes hull interaction amplification of transverse rudder force:

```text
F_Y_total = (1 + a_H) * F_Y_rudder
```

with an empirical `a_H` depending on draft, chord, and distance from rudder leading edge to hull aft end. The center of effort may shift forward, changing the yaw moment lever arm.

Raw locator: Bertram §5.4.5, printed pp.193-195.

## Related pages

- [[maneuvering-coordinate-conventions]]
- [[yaw-moment-rudder-sweep]]
- [[environmental-yaw-moment-coefficients]]
