---
name: crossprovider codex text-hash-dedup-for-versioned-documents
description: Text-hash dedup for versioned documents
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [pdf-ingest, deduplication, versioned-content]
---

When ingesting versioned documents (standards, drafts, editions), byte-different files may have identical extracted text. Always hash the full extracted-text output and compare against existing content before writing; this catches duplicates that filename/size comparison misses. The ISO 19905-1 and DIS 1099 families contained multiple editions that would have created corrupt duplicate pages without text-hash dedup.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
