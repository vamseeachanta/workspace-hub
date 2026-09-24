---
name: crossprovider codex standards-edition-choice-must-be-consistent-acro
description: Standards edition choice must be consistent across code, tests, and resolver metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards, metadata, versioning, traceability]
---

When a standard has multiple editions (DNV-RP-F106 2003 vs. 2021-09), the choice is driven by explicit scope (GitHub issue) and local source availability. The implementation, tests, and wiki resolver must all cite the same revision. Divergence (e.g., code cites 2003, tests assume 2021-09 data) breaks verification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
