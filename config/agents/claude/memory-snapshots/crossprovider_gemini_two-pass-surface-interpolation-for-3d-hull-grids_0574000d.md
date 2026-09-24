---
name: crossprovider gemini two-pass-surface-interpolation-for-3d-hull-grids
description: Two-pass surface interpolation for 3D hull grids
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [numerical-methods, hull-modeling, interpolation]
---

Decompose 3D interpolation into two passes: (1) interpolate each station's z-profile to common z_grid using 1D PCHIP, (2) interpolate each z-row along-x using B-spline. Modular strategy enables monotonicity control per-station and simplifies numerical handling of geometry discontinuities.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
