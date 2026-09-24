---
name: crossprovider codex field-aliases-in-existing-mappings-can-be-silent
description: Field aliases in existing mappings can be silently dropped during refactors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [refactoring, testing, backward-compatibility]
---

Existing code may support CYCLE_YEAR/CYCLE_MONTH aliases alongside production_date. Refactors that consolidate to production_date only silently break the alias path. Explicitly test that refactors preserve old field-name support.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
