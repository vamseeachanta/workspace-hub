---
name: crossprovider codex verification-commands-in-plans-must-be-literally
description: Verification commands in plans must be literally reproducible
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [plan-review, verification, reproducibility]
---

A plan's verification section contained a Python code block claiming it would produce `snapshot-issue` and `snapshot-url` output, but executing that exact block produced nothing. Non-reproducible proofs in plan acceptance criteria fail adversarial review because they cannot be verified independently. All verification steps must execute to their stated outputs when run verbatim.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
