---
name: crossprovider codex deduplication-gate-before-write
description: Deduplication gate before write
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, data-integrity, write-gate]
---

Query target domain's standards/ and sources/ directories by code_id/title before creating any page. If a match exists, augment it in-place instead of creating a duplicate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
