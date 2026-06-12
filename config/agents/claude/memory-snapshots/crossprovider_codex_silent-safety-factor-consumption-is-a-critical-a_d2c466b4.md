---
name: crossprovider codex silent-safety-factor-consumption-is-a-critical-a
description: Silent safety-factor consumption is a critical architectural blocker
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [safety, standards, architectural, digitalmodel, design-defect]
---

When design parameters (e.g., safety factors 1.67/1.25) are defined on a model but never consumed by any calculation method, it creates a silent divergence hazard. MooringLineDesign exposed safety_factor fields but check_mbl() never divided by them; this is MAJOR in planning and requires explicit wiring into at least one consumer before code review approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
