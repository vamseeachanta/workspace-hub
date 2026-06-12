---
name: crossprovider codex formal-state-model-clarifies-migration-idempoten
description: Formal state model clarifies migration idempotency
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [migrations, state-machine, idempotence]
---

Migrations benefit from explicit state naming (pre-wave, wave-applied, partial-applied) to reason about idempotence, rollback safety, and collision detection. Vague state language ('clean tree', 'ready') hides assumptions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
