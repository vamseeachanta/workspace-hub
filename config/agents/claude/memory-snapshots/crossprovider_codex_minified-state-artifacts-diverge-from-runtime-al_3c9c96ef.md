---
name: crossprovider codex minified-state-artifacts-diverge-from-runtime-al
description: Minified state artifacts diverge from runtime; always verify with generators
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifact-verification, configuration-management, state-consistency]
---

Complex shared state (cron registries, scheduler configs) stored as minified JSON text artifacts can stale without runtime verification. Never trust artifact text for correctness; always run the generator/checker against current state. Text can be commit-stale while runtime evolves.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
