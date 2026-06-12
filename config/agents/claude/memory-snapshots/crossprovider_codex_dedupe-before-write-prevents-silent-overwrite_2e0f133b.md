---
name: crossprovider codex dedupe-before-write-prevents-silent-overwrite
description: Dedupe-before-write prevents silent overwrite
metadata:
  type: reference
  source: codex
  bridged: 2026-05-28
  tags: [deduplication, content-integrity, scale-safety]
---

Before creating or overwriting any page, grep the target domain's standards/ and sources/ for an existing page on the same code_id. If found, augment in place (add missing sections/tables), do not overwrite or duplicate. Report every dedupe hit.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
