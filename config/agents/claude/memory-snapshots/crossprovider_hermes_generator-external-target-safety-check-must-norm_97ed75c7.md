---
name: crossprovider hermes generator-external-target-safety-check-must-norm
description: Generator external-target safety check must normalize prefix consistently
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [generator, link-safety, prefix-normalization]
---

External links can be silently dropped if prefix handling diverges between `is_safe_external_target()` check and `add_edge()` normalization. Inconsistency ('external.' vs 'external') causes undetectable link loss.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
