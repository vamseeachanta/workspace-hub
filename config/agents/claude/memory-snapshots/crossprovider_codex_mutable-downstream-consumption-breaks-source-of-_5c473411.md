---
name: crossprovider codex mutable-downstream-consumption-breaks-source-of-
description: Mutable downstream consumption breaks source-of-truth reproducibility
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [versioning, downstreams, reproducibility]
---

Publishers that download and patch from live external services (e.g., HF main branch) are not reproducible from repository sources alone. Pinned versions must be stored in a durable registry controlled by the producer, never mutated in-place by consumers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
