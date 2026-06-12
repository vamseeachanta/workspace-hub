---
name: crossprovider hermes documentation-stale-reference-drift-requires-lin
description: Documentation stale-reference drift requires lint gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [documentation, lint, drift-detection]
---

README still referenced removed directory paths; manual docs updates lag code moves. Add CI lint rules grepping docs for removed paths; run before merge to catch drift early.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
