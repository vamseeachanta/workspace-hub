---
name: crossprovider codex dedupe-before-write-search-target-domain-before-
description: Dedupe-before-write: search target domain before creating any wiki page
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ingest-contract, deduplication, wiki-maintenance]
---

Before writing a new standards page, grep target domain's standards/ and sources/ for existing pages by code_id and title. If found, augment in place (add missing sections/tables) rather than create duplicate. This prevents systematic duplication across large ingest batches.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
