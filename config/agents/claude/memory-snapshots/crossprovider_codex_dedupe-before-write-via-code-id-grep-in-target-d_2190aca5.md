---
name: crossprovider codex dedupe-before-write-via-code-id-grep-in-target-d
description: Dedupe-before-write via code_id grep in target domain
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards-ingest, deduplication, grep-pattern]
---

Before creating/editing standards pages, grep target domain's standards/ + sources/ for existing page by code_id. Augment in place; never create duplicate. Existing source indices (og-standards-iso.md) provide pre-seeded dedupe reference, reducing manual lookup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
