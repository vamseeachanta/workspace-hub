---
name: crossprovider codex deduplication-keys-must-be-root-independent
description: Deduplication keys must be root-independent
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, data-model, source-reconciliation]
---

When deduplicating mirrored sources from different roots, the dedup key must use publisher+designation+edition+source_fingerprint, not path-dependent source_id. Issue #508 showed identical B31.3 sources from og-asme and og-raw-asme were treated as distinct without a root-independent key.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
