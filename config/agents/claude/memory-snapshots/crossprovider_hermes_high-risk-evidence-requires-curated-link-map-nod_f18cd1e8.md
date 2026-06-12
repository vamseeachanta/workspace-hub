---
name: crossprovider hermes high-risk-evidence-requires-curated-link-map-nod
description: High-risk evidence requires curated link-map node validation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [graph-validation, access-control, public-surface]
---

High-risk evidence must resolve through an allowlisted curated basename to a graph node with `kind == 'link_map'` and `is_curated: true`, not just basename matching. Validation enforces allowlist + emitted-node resolution in tight coupling.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
