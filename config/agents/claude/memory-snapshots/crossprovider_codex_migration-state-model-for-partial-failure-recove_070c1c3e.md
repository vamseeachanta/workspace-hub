---
name: crossprovider codex migration-state-model-for-partial-failure-recove
description: Migration state model for partial-failure recovery
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migration, state-machine, patterns]
---

Three states: pre-wave (no targets), wave-applied (complete), partial-applied (mixed). Rollback must run before retry from partial-applied state. Enables safe restart and prevents corrupted mixed-state migrations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
