---
name: crossprovider hermes plan-readme-index-is-canonical-state-for-per-pla
description: Plan README index is canonical state for per-plan status; drift silently breaks approval gates
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [planning, gates, index-management]
---

When plan draft/review/approved status drifts between per-plan files and README index, approval gates operate on stale state. README must be kept in sync as single source of truth.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
