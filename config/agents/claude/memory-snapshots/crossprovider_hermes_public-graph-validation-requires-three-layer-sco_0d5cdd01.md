---
name: crossprovider hermes public-graph-validation-requires-three-layer-sco
description: Public graph validation requires three-layer scope enforcement
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [public-graph, scope-gate, access-control]
---

Generator and validator must mirror identical scope gates: exclude private, raw, and agent-specific surfaces. Three-layer check (surface-kind, evidence linking, freshness) prevents leakage of internal/unreviewed artifacts to public graph.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
