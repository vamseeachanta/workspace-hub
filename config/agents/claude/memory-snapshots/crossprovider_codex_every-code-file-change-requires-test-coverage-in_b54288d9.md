---
name: crossprovider codex every-code-file-change-requires-test-coverage-in
description: Every code file change requires test coverage; integration points and shell wiring are no exception
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, testing, hard-gate]
---

Dashboard/shell integration changes, helper library additions, and config wiring modifications must have corresponding tests. The TDD gate applies uniformly; integration tests are not optional.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
