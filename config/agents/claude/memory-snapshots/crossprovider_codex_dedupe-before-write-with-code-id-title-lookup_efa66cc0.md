---
name: crossprovider codex dedupe-before-write-with-code-id-title-lookup
description: Dedupe-before-write with code_id/title lookup
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [standards-ingest, deduplication]
---

Search target domain's standards/ and sources/ by code_id and title before creating any page; if found, augment in place (add missing sections/tables) rather than overwrite wholesale or duplicate. Require dedupe-hit reporting per implementation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
