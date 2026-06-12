---
name: crossprovider codex dedupe-before-write-gate-prevents-duplicate-page
description: Dedupe-before-write gate prevents duplicate pages across concurrent batches
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [pdf-ingest, deduplication, workflow]
---

Before writing any page, grep target domain's standards/ + sources/ for code_id match. If found, augment in place (add sections/tables) rather than overwrite or duplicate. Critical for parallel ingest worktrees.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
