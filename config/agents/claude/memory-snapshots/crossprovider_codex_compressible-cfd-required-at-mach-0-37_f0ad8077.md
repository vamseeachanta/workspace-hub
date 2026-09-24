---
name: crossprovider codex compressible-cfd-required-at-mach-0-37
description: Compressible CFD required at Mach 0.37
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [cfd, aerodynamics, vehicle-dynamics]
---

For vehicles cruising at 285 mph (~Mach 0.37), compressible CFD must be used instead of scaling incompressible simpleFoam coefficients. Published ground-effect research shows relevant compressibility effects below Mach 0.15, especially around wheels and underfloors. Incompressible models cannot capture these effects accurately.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
