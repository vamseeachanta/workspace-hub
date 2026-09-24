---
name: crossprovider codex page-local-source-tables-must-align-with-schema-
description: Page-local source tables must align with schema contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-validation, schema-consistency, testing]
---

When wiki pages include their own `## Sources` sections, they must match the central source-map schema (required fields, non-empty `accessed` dates, `intended_use`, `visible_version_or_date`). Tests should parse and validate every source-row field, not just check URL membership or table shape.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
