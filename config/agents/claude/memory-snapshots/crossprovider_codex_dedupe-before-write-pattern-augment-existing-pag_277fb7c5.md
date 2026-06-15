---
name: crossprovider codex dedupe-before-write-pattern-augment-existing-pag
description: Dedupe-before-write pattern: augment existing pages rather than duplicate
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [extraction, deduplication, augmentation]
---

Before creating any new wiki page, grep the target domain's standards/ and sources/ for an existing page by code_id and title. If found, augment in place (add missing parts/tables). If thin from a prior shallow pass, add full-text parts. Never create duplicates.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
