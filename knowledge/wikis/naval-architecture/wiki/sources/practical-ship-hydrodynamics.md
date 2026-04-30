---
title: "Practical Ship Hydrodynamics"
author: "V. Bertram"
year: 2000
size_mb: 2.2
topics: ["hydrodynamics", "resistance", "propulsion", "seakeeping", "maneuvering", "rudder"]
type: hydrostatics
source: naval-architecture-resources.yaml
sources:
  - "/mnt/ace/O&G-Standards/SNAME/hydrostatics-stability/Practical-Ship-Hydrodynamics-Bertram-2000.pdf"
added: 2026-04-07
last_updated: 2026-04-30
tags: [hydrostatics, naval-architecture, hydrodynamics, resistance, maneuvering, rudder]
---

# Practical Ship Hydrodynamics

## Summary

| Property | Value |
|----------|-------|
| Author | V. Bertram |
| Year | 2000 |
| Size | 2.2 MB |
| Type | hydrostatics |
| Topics | hydrodynamics, resistance, propulsion, seakeeping, CFD, rudder/maneuvering |
| Raw path | `/mnt/ace/O&G-Standards/SNAME/hydrostatics-stability/Practical-Ship-Hydrodynamics-Bertram-2000.pdf` |

## Notes

Practical engineering approach to ship hydrodynamics.

## Yaw/rudder extraction for #2564

Section 5.4.2, printed pp.181-185, provides rudder lift/drag/moment coefficient definitions and warns that simple estimates are rough for ship rudders due to irregular inflow, turbulence, Reynolds-number differences, and hull/propeller interaction.

Key formulas and facts retained in [[rudder-force-modeling]]:

- `C_L = L/(q A_R)`
- `C_D = D/(q A_R)`
- `C_QN = Q_N/(q A_R c_m)`
- `C_QR = Q_R/(q A_R c_m)`
- `q = 0.5 rho V^2`
- `delta_eff = (2.2 Lambda/(Lambda + 2.4)) delta`
- typical ship-rudder `1.2 < C_L,max < 1.4`

Section 5.4.4 gives propeller-slipstream corrections; §5.4.5 gives rudder-hull interaction and center-of-effort-shift cautions. These are upgrade paths beyond the first #2564 sweep.

Related: [[rudder-force-modeling]], [[yaw-moment-rudder-sweep]].
