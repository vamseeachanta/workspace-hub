---
name: crossprovider codex adversarial-plan-review-finds-sentinel-value-fil
description: Adversarial plan review finds sentinel-value filtering gaps in mesh handlers
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [mesh-utilities, data-structure-quirks, schema-contracts]
---

When plans operate on mesh data, they must account for sentinel values used internally by mesh libraries (e.g., `-1` padding in triangle rows). Generic consumers reusing mesh library fields without filtering sentinels produce false findings. Verify sentinel-aware filtering in pseudocode and test coverage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
