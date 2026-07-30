---
name: crossprovider codex aggregating-internal-component-details-hides-rec
description: Aggregating internal component details hides reconciliation information
metadata:
  type: reference
  source: codex
  bridged: 2026-07-16
  tags: [data-aggregation, fdas]
---

V30 calculates facility subcomponents internally but emits only aggregate cost, breaking downstream reconciliation. Report generation silently defaults components to zero when they cannot be recovered from aggregates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
