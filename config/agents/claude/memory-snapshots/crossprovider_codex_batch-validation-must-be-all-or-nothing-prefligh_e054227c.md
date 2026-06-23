---
name: crossprovider codex batch-validation-must-be-all-or-nothing-prefligh
description: Batch validation must be all-or-nothing preflight before any writes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [batch-processing, data-integrity, validation-pattern]
---

Validating batch items per-item during write loops leaves partial state on late failures. Must validate entire batch identity, duplicates, target paths, and schema at load time before entering the write phase. Enables rollback/retry without cleanup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
