---
name: crossprovider codex tdd-evidence-requires-meaningful-behavioral-fail
description: TDD evidence requires meaningful behavioral failures, not syntax/import errors
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [testing, tdd, methodology]
---

"Tests must be red" without a meaningful behavioral failure is theater. Red from syntax, missing imports, or env setup does not prove behavior-first TDD. Correct: define failing assertion before implementation, capture behavioral failure output, show same test passing after.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
