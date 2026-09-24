---
name: crossprovider codex inertia-tensor-origin-frame-must-be-tracked-expl
description: Inertia tensor origin frame must be tracked explicitly
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [physics, schema-precision, diffraction]
---

When computing inertia tensors from empirical radii, the origin reference frame (body_origin vs centre_of_mass) must match the schema's declared origin. Mismatches produce physically incorrect hydrodynamic models even if numerically valid.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
