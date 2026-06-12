---
name: crossprovider codex tdd-pattern-for-bounded-approved-fixes-validates
description: TDD pattern for bounded approved fixes validates scope
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [tdd-pattern, approved-fixes, scope-control]
---

Write failing contract tests that expose the approved gap, confirm RED state, implement minimal code to pass GREEN, then validate via diff and broader regression suites. This produces explicit proof of the gap and the fix, keeping changes naturally scoped.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
