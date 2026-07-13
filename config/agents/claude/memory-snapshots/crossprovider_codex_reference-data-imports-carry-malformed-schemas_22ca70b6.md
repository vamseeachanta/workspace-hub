---
name: crossprovider codex reference-data-imports-carry-malformed-schemas
description: Reference data imports carry malformed schemas
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [data-quality, schema-validation, imports, publishing]
---

Discovered source datasets (SQL corpus, spreadsheet reference data) often contain malformed DDL, duplicate table definitions, or broken constraints even if structurally complete (files exist, parse). Validate against canonical domain schema and normalize before committing to publishing pipeline; assume raw imports need remediation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
