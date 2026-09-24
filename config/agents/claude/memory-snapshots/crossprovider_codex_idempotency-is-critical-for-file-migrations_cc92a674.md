---
name: crossprovider codex idempotency-is-critical-for-file-migrations
description: Idempotency is critical for file migrations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [migrations, data-integrity, idempotency]
---

Migration scripts must be designed so that running `--apply` twice on a clean migrated state produces zero content differences. This property prevents silent data corruption and enables safe retry workflows after partial failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
