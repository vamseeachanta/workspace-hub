---
name: crossprovider codex multi-pass-data-enrichment-compute-order-matters
description: Multi-pass data enrichment: compute order matters for dependent fields
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [data-pipeline, enrichment, ordering]
---

Session 16 found HULL_LIBRARY_REF assigned before dimensions estimated, leaving generic refs permanent even after LOA populated. For dependent fields (e.g., hull ref depends on estimated LOA), either defer assignment until dependencies ready or regenerate when dependency becomes available.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
