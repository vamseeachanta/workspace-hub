---
title: "Simulation of Hydrodynamic Forces and Motions for a Freely Maneuvering Ship in a Seaway"
tags: [maneuvering, shipmo3d, rudder, validation]
sources:
  - /mnt/ace/digitalmodel/docs/ship-design/literature/maneuvering_ship.pdf
added: 2026-04-30
last_updated: 2026-04-30
---

# Simulation of Hydrodynamic Forces and Motions for a Freely Maneuvering Ship in a Seaway

Raw path: `/mnt/ace/digitalmodel/docs/ship-design/literature/maneuvering_ship.pdf`

## Relevance

Implementation-oriented ShipMo3D report useful for future upgrades from [[yaw-moment-rudder-sweep]] toward full maneuvering simulation.

## Key extracted content

- §3 / Figure 5 defines turning-circle validation metrics: advance, transfer, tactical diameter.
- §4, printed pp.8-10, gives hull maneuvering force model with normalized `v'` and `r'` and nonlinear coefficient terms.
- §8, printed p.16, gives rudder-deflection force assembly and `F_N^rudder` projection.
- §9, printed pp.16-17, gives propeller-rudder interaction lift/drag corrections consistent with Bertram.
- Table 14, printed p.30, shows sensitivity of turning predictions to `C_rudder-prop`: changing from 0.5 to 0.2 increased tactical diameter about 12%; changing to 0.8 reduced it about 8%.
- §11, printed pp.19-23, includes Esso Osaka validation inputs and turning-circle comparison.

## Implementation caution

`F_N^rudder` in ShipMo3D is not just a standalone lift formula; it is assembled from damping/stiffness terms and projected using rudder dihedral. Use it as a future higher-fidelity reference, not a replacement for the bounded #2564 first-pass sweep.

Related: [[rudder-force-modeling]], [[maneuvering-validation-metrics]].
