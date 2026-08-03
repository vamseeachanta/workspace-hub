---
name: crossprovider codex transonic-vehicle-cfd-at-mach-0-37-requires-comp
description: Transonic vehicle CFD at Mach 0.37+ requires compressible full-motion-ground solver
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [aero, cfd, compressibility, transonic, gt-r, ground-effect]
---

At 285 mph (~Mach 0.37), low-speed passenger-car aerodynamic coefficients are not defensible. Compressibility effects appear below Mach 0.15 in ground-effect studies; moving ground, wheel rotation, actual tire/rim geometry, ride height, and yaw/pitch must be modeled together as a coupled system. A simple dynamic-pressure scaling of low-speed C_D, C_L, or C_PM is incorrect—the sign of drag change itself is configuration-dependent.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
