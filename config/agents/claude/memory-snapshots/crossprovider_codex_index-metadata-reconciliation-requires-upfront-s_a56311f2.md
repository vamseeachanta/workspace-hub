---
name: crossprovider codex index-metadata-reconciliation-requires-upfront-s
description: Index metadata reconciliation requires upfront strategy
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [documentation, data-integrity, metadata-management]
---

When maintaining counter fields in documentation (e.g., `source_count`, `page_count`), decide explicitly: reconcile to ground-truth file count once, OR increment numerically on each edit. Mixing both creates drift. If existing counters are deflated, a one-time reconciliation is safer than continuing incremental updates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
