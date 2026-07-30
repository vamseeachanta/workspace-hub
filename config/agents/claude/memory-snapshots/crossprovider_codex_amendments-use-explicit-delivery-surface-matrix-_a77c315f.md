---
name: crossprovider codex amendments-use-explicit-delivery-surface-matrix-
description: Amendments: use explicit delivery-surface matrix to track completeness
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [amendments, completeness-tracking, implementation-planning, audit]
---

For large amendments with multiple delivery surfaces (code, tests, docs, enforcement, CI, wrappers), create an explicit presence/absence matrix early. Example: 40-row amendment → 19 surfaces present, 21 missing (20 engineering deferred + 1 approval marker). Separates 'not yet delivered' from 'deliberately deferred' and clarifies implementation order.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
