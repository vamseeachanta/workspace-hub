---
name: crossprovider codex composite-mutations-need-explicit-tdd-guard-test
description: Composite mutations need explicit TDD guard tests
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [tdd-patterns, regression-tests, multi-field-validation]
---

Single-field mutation tests miss bugs where multiple related fields are inverted together (e.g., both issue IDs swapped in #66/#67); regression guards must cover composite cases and cross-field consistency.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
