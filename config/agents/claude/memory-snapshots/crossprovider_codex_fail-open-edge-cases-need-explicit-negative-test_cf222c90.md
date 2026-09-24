---
name: crossprovider codex fail-open-edge-cases-need-explicit-negative-test
description: Fail-open edge cases need explicit negative tests
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, tdd, edge-cases]
---

Patterns like empty suffixes (req-/prj- + empty string) and fail-open boundary conditions slip through positive-only TDD. Add negative test cases that explicitly verify rejection of these variants before moving to the next gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
