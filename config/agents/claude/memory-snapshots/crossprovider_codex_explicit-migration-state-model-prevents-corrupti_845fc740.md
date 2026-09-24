---
name: crossprovider codex explicit-migration-state-model-prevents-corrupti
description: Explicit migration state model prevents corruption
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migrations, state-management, safety-pattern]
---

Define explicit states (pre-wave, wave-applied, partial-applied) to track multi-stage migrations. This prevents partial failures and enables safe rollback; second applies in wave-applied state must be no-ops to ensure idempotency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
