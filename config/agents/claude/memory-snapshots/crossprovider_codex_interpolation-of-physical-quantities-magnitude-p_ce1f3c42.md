---
name: crossprovider codex interpolation-of-physical-quantities-magnitude-p
description: Interpolation of physical quantities (magnitude/phase separately) mishandles discontinuities and response zeros
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hydrodynamics, interpolation, signal-processing, solver-comparison]
---

Interpolating magnitude and wrapped phase independently can cross phase discontinuities and mishandle zeros in the complex transfer function. Equivalent solvers with different grid spacing will produce degraded correlation metrics when interpolated separately. Use complex-valued interpolation on the union grid or evaluate on a common declared grid, not magnitude and phase in isolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
