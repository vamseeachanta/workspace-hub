---
name: crossprovider codex explicit-precondition-assertions-prevent-test-fa
description: Explicit precondition assertions prevent test false-positives
metadata:
  type: reference
  source: codex
  bridged: 2026-07-19
  tags: [testing, assertions, preconditions]
---

Tests should assert their preconditions (shallow repository, one-parent HEAD, absent producer objects) before running the operation, rather than relying on implicit setup. Refactored code can accidentally satisfy broad assertions via wrong paths; explicit topology checks catch this.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
