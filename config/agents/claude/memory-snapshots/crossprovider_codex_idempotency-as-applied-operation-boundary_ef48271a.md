---
name: crossprovider codex idempotency-as-applied-operation-boundary
description: Idempotency as applied operation boundary
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration-strategy, safety]
---

Require that apply operations be idempotent: running apply twice on clean migrated state must produce zero content diff. Prevents accidental re-runs and other manual recovery attempts from causing damage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
