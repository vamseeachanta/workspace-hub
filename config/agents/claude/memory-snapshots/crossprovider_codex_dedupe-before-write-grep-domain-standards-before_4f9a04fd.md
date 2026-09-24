---
name: crossprovider codex dedupe-before-write-grep-domain-standards-before
description: Dedupe-before-write: grep domain standards before creating pages
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deduplication, write-safety, dedupe-workflow]
---

Before writing any new standard/source page, grep the TARGET domain's standards/ and sources/ directories for existing pages on the same code_id/title. If found, augment in place (add missing sections/tables); never overwrite wholesale or create duplicates. Report every dedupe hit and action taken.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
