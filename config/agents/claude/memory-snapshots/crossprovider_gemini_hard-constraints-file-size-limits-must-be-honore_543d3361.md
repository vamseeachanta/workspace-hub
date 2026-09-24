---
name: crossprovider gemini hard-constraints-file-size-limits-must-be-honore
description: Hard constraints (file size limits) must be honored in the same PR
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [constraints, architecture, code-review]
---

A 400-line file-size limit exists for maintainability. Violating it with 509 lines and deferring refactoring to 'future work' undermines the constraint. Refactor (extract to separate module) in the PR that would exceed the limit.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
