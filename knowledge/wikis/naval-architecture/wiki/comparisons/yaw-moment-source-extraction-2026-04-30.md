---
title: "Yaw Moment Source Extraction — 2026-04-30"
tags: [yaw, rudder, maneuvering, source-extraction]
sources:
  - pna-vol-iii-motions-controllability
  - usna-en400-principles-ship-performance-2020
  - practical-ship-hydrodynamics-bertram-2000
  - mctaggart-shipmo3d-maneuvering-2007
  - abs-vessel-maneuverability-guide-2017
  - imo-msc-circ-1053-manoeuvrability-explanatory-notes
  - uscg-nvic-6-95-maneuvering-standards
  - uscg-nvic-7-89-maneuvering-information
  - orcaflex-manoeuvring-current-wind-loads
  - ocimf-yaw-moment-coefficient-figures
added: 2026-04-30
last_updated: 2026-04-30
---

# Yaw Moment Source Extraction — 2026-04-30

This page preserves the raw-reference review context for issue #2564 so the implementation phase does not lose source provenance.

## Source set reviewed

| Source | Raw path | Primary use |
|---|---|---|
| PNA Vol. III — Motions and Controllability | `/mnt/ace/O&G-Standards/SNAME/textbooks/Principles-of-Naval-Architecture-SecondRevision-Vol3-Motions-Controllability.pdf` | controllability, rudder sign convention, control-surface geometry, yaw/sway equations |
| USNA EN400 — Principles of Ship Performance | `/mnt/ace/O&G-Standards/SNAME/textbooks/USNA-EN400-Principles-Ship-Performance-2020.pdf` | ship axes/DOF, maneuverability, rudder angle/speed/dimension dependence |
| Bertram — Practical Ship Hydrodynamics | `/mnt/ace/O&G-Standards/SNAME/hydrostatics-stability/Practical-Ship-Hydrodynamics-Bertram-2000.pdf` | rudder coefficients, stall, propeller/hull interaction |
| McTaggart ShipMo3D report | `/mnt/ace/digitalmodel/docs/ship-design/literature/maneuvering_ship.pdf` | hull maneuvering forces, `F_N^rudder`, propeller-rudder interaction, validation |
| ABS Guide for Vessel Maneuverability | `/mnt/ace/acma-codes/ABS Rules/Vessel Maneuverability/Vessel_Maneuverability_Guide_e-Feb17.pdf` | 3-DOF equations, linear rudder inputs, state-space form, ratings |
| IMO MSC/Circ.1053 | `/mnt/ace/acma-codes/IMO/Maneouvrability/2002 MSC Circ.1053 Explanatory Notes to Manoeuvrability.pdf` | yaw-rate/rudder-angle relation, spiral loop, standard conditions |
| USCG NVIC 6-95 | `/mnt/ace/acma-codes/USCG/NVIC's/1995 NVIC 6-95 Maneuvering Standards.pdf` | IMO criteria and USCG context |
| USCG NVIC 7-89 | `/mnt/ace/acma-codes/USCG/NVIC's/1990 NVIC 7-89 Maneuvering Information.pdf` | pilot card / wheelhouse poster / maneuvering booklet context |
| OrcaFlex vessel theory pages | `/mnt/ace/digitalmodel/llm-wiki/orcaflex/topics/` | environmental yaw moments, Munk moment double-counting |
| OCIMF yaw coefficient figures | `/mnt/ace/acma-codes/OCIMF/Figures/` | current/wind yaw coefficient curve families |

## Implementation-critical facts retained

1. **Coordinate convention**: EN400 says `x` forward, `y` starboard, yaw about `z`; PNA says positive stern-rudder deflection corresponds to a port turn.
2. **Preliminary #2564 formula**: direct rudder yaw moment can be represented as `M_z = F_N * x_rudder_from_CG`, but this is not a full maneuvering model.
3. **Speed scaling**: rudder force depends on dynamic pressure and therefore scales with `V^2` in simple pre-stall models.
4. **Angle range**: typical rudder range about `±35°`; stall becomes important near 40-45°.
5. **Geometry**: span, chord, area, aspect ratio, and stock/center-of-pressure definitions matter.
6. **Propeller effects**: slipstream can more than double rudder force; Bertram/ShipMo3D provide correction forms but interaction coefficient is uncertain.
7. **Hull effects**: hull can amplify transverse rudder force and shift center of effort, changing yaw lever arm.
8. **Full model**: ABS/PNA linearized sway-yaw equations and hydrodynamic derivatives are future upgrades.
9. **Validation**: IMO/USCG/ABS metrics validate maneuvering simulations, not a standalone yaw-force sweep.
10. **Environmental yaw**: OCIMF current/wind yaw coefficients are angle-dependent curve families and must not be blindly summed with manoeuvring Munk terms.

## Pages created from this extraction

- [[maneuvering-coordinate-conventions]]
- [[rudder-force-modeling]]
- [[yaw-moment-rudder-sweep]]
- [[maneuvering-validation-metrics]]
- [[environmental-yaw-moment-coefficients]]
- source pages for ABS, IMO, USCG, ShipMo3D, OrcaFlex/OCIMF

## Remaining extraction gaps

- Numeric digitization of OCIMF yaw coefficient curves was not performed.
- Exact Bertram hull-interaction signs must be aligned to the codebase convention before implementation.
- Full PNA/ABS hydrodynamic-derivative simulation is deliberately out of scope for the first #2564 implementation.
