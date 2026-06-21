---
name: crossprovider codex row-equality-validation-requires-normalization-a
description: Row equality validation requires normalization and sorting
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [data-validation, testing, canonicalization]
---

When comparing generated ledgers/reports to canonical sources, enforce strict equality after sorting by ID rather than just set membership checks. This catches subtle row corruption, dropped rows, and missing hashes that set checks would miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
