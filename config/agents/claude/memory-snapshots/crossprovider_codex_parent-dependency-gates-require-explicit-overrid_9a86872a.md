---
name: crossprovider codex parent-dependency-gates-require-explicit-overrid
description: Parent-dependency gates require explicit override syntax
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, gate-enforcement]
---

When a plan has a parent issue blocker (child #706 blocked by parent #703), state the dependency in scope, enforce it in gate checks, and require an explicit verbatim user override like 'I explicitly override the #703 parent dependency for child #706' for progression. Implementers need unambiguous control flow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
