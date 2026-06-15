---
name: crossprovider codex dedupe-before-write-is-a-mandatory-pre-write-gat
description: Dedupe-before-write is a mandatory pre-write gate, not post-hoc cleanup
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [ingest-contract, deduplication, write-safety]
---

Before creating any page, grep the target domain's standards/ and sources/ for existing pages on the same standard (by code_id and title). If found, augment in place (add missing sections/tables, do NOT overwrite wholesale). This prevents fragmentation, duplicate work, and inconsistent surfaces. Report every dedupe hit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
