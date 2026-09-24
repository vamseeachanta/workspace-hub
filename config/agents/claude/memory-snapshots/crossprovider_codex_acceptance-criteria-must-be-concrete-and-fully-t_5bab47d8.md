---
name: crossprovider codex acceptance-criteria-must-be-concrete-and-fully-t
description: Acceptance criteria must be concrete and fully tested
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [acceptance-criteria, test-coverage, scope-clarity]
---

Range-based criteria like 'at least two of {X, Y, Z}' mask test coverage gaps and allow incomplete implementations. Criteria must enumerate exact surface (target types, file paths, rules) and tests must verify all criteria, not a subset. Observed in #2408 where acceptance criteria and test list diverged.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
