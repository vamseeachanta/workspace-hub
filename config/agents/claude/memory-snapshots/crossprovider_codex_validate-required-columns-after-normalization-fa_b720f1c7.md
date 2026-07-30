---
name: crossprovider codex validate-required-columns-after-normalization-fa
description: Validate required columns after normalization, fail closed
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [data-validation, source-verification, fail-closed]
---

Nonempty but unusable ZIP members (wrong columns, parse failures) produce rows with blank identifiers and zero volumes. They appear 'valid' but corrupt aggregates. After normalization, verify canonical columns (date + stable key + volume) exist before writing output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
