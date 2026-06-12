---
name: crossprovider codex tdd-red-phases-must-be-falsifiable-with-pre-chan
description: TDD red phases must be falsifiable with pre-change failures
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [tdd, testing, verification]
---

Plans claiming to fix a known failure should define the pre-change command that fails. If the test passes before code changes, there is no red phase and the plan hasn't proven the fix was needed.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
