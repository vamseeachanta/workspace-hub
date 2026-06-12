---
name: crossprovider codex dedupe-before-write-augment-existing-pages-never
description: Dedupe-before-write: augment existing pages, never create duplicates
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [content-integrity, ingest, deduplication]
---

Before creating any page, grep the target domain's standards/ and sources/ for existing pages by code_id and title. If found, augment in place rather than create a duplicate. This is non-obvious and critical for maintaining single source of truth in the corpus.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
