---
name: crossprovider hermes simulation-physics-verification-requires-separat
description: Simulation physics verification requires separate boundary-state + final-output testing
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, simulation, physics]
---

Transient/discretized simulations need two test layers: (1) structural (endpoint exists, arrays have right length) and (2) physics-specific (final state computed with correct remainder integration, force/acceleration values correct at boundaries). One layer alone misses bugs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
