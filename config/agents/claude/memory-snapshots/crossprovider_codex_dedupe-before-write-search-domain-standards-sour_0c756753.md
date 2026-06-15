---
name: crossprovider codex dedupe-before-write-search-domain-standards-sour
description: Dedupe-before-write: search domain standards/ + sources/ by code_id
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [corpus-ingest, deduplication]
---

Before creating a standard page, grep target domain for existing page by code_id. If found, augment in place; never create duplicate. Prevents redundant extraction and version confusion in corpus.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
