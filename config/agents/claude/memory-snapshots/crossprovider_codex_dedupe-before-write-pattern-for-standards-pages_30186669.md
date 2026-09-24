---
name: crossprovider codex dedupe-before-write-pattern-for-standards-pages
description: Dedupe-before-write pattern for standards pages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, data-quality, standards-ingestion]
---

Grep target domain's standards/ + sources/ for existing pages by code_id before creating new ones. On hits, augment in place rather than overwrite wholesale. Prevents duplicate/variant resolver-page pollution.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
