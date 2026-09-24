---
name: crossprovider codex tests-need-explicit-failure-modes-not-generic-de
description: Tests need explicit failure modes, not generic descriptors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-design, test-specificity, acceptance-criteria]
---

Tests described as 'representative' or 'comprehensive' are too vague to verify. Better: concrete test cases with explicit inputs and expected outcomes ('should fail when X is absent, pass when X is present'). Vague test language hides approval blockers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
