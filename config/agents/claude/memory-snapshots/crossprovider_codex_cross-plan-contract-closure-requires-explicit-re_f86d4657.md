---
name: crossprovider codex cross-plan-contract-closure-requires-explicit-re
description: Cross-plan contract closure requires explicit registry/manifest surfaces
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [architecture, governance, planning]
---

Multi-issue plans that depend on identity registries (e.g., `cost_requirement_identity.csv`, `cost_event_identity.csv`) must explicitly extend those surfaces and versioning contracts at every plan boundary, or downstream plans cannot satisfy monotonic issuance, collision, and migration guarantees. Implicit alignment fails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
