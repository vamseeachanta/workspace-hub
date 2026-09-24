---
name: crossprovider codex review-verdict-scope-is-determined-by-implementa
description: Review verdict scope is determined by implementation artifact accessibility
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-process, methodology]
---

If a code review cannot access the implementation diff (local sandbox failure, missing file), verdict must be MAJOR because safety/correctness cannot be verified. GitHub connector can substitute for local access when local shell execution fails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
