---
name: crossprovider codex fail-closed-standards-derived-coefficient-sourci
description: Fail-Closed Standards-Derived Coefficient Sourcing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [standards, coefficients, licensed-sources, fail-closed]
---

When implementing calculations from licensed standards/workbooks (e.g., OCIMF), emit fail-closed Citation sidecars per `.claude/rules/calc-citation-contract.md`, never commit sources, and block implementation if verification fails rather than inventing fallback data.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
