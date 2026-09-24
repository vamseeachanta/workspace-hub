---
name: crossprovider codex content-validation-must-check-required-schema-no
description: Content validation must check required schema, not just file structure
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-validation, schema, defect-class]
---

A ZIP member that parses as CSV but lacks required columns produces rows with blank identifiers and zero volumes, appearing valid to envelope-only checks. Validation must confirm required canonical columns exist after parsing, not just that the file is readable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
