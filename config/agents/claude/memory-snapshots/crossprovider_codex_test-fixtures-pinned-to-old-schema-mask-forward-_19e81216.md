---
name: crossprovider codex test-fixtures-pinned-to-old-schema-mask-forward-
description: Test fixtures pinned to old schema mask forward-compatibility regressions
metadata:
  type: reference
  source: codex
  bridged: 2026-07-24
  tags: [schema-migration, test-fixtures, integration-testing, equality-matrix]
---

Provider-row test fixtures staying on schema 4 while the collector moves to schema 5 create a false-pass: unit tests assert correctness but integration breaks silently. Fixtures should track the same schema version as the production emitter, not stay pinned to the previous version.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
