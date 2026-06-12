---
name: crossprovider hermes hydrodynamic-matrices-not-symmetric-use-relative
description: Hydrodynamic matrices not symmetric; use relative tolerance
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hydrodynamics, validation, tolerance]
---

6×6 coupled hydrodynamic matrices (added mass, damping) are not perfectly symmetric due to cross-coupling effects. Validation tests using exact equality fail; require relative tolerance (~0.5-1%) for realistic data. Important for solver handoff validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
