---
name: crossprovider codex edge-case-test-coverage-gaps-around-metadata-def
description: Edge-case test coverage gaps around metadata defaults and missing fields
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, coverage, edge-cases]
---

Unit tests pass for happy paths but miss edge cases triggered by missing optional fields, undeclared categories, and implicit fallback logic. Examples: missing prior ledgers ignored silently, parent alias hiding undeclared sibling folders, explicit non-PDF kinds defaulting wrong. Require `/tmp` fixture reproduction for edges; add regression tests for discovered edge cases with explicit fail-closed assertions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
