---
name: crossprovider codex idempotent-apply-is-non-negotiable-for-multi-wav
description: Idempotent apply is non-negotiable for multi-wave migrations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [idempotency, migration-pattern, state-management]
---

Second `--apply` on completed state must produce zero content diff, enabling safe retry loops and rollback+reapply workflows without re-migrating already-centralized specs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
