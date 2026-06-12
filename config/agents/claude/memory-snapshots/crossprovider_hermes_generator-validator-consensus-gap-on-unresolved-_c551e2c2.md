---
name: crossprovider hermes generator-validator-consensus-gap-on-unresolved-
description: Generator/validator consensus gap on unresolved edges
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, generator, consensus-gap, edge-semantics]
---

Generator includes ALL unresolved targets in summary (including dropped unsafe ones that don't emit edges); validator only computes unresolved from emitted edges. Causes count mismatches and false-pass validation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
