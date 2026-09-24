---
name: crossprovider codex test-coverage-gaps-for-new-code-paths-must-be-ex
description: Test coverage gaps for new code paths must be explicit in acceptance criteria
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, acceptance-criteria, coverage]
---

WRK-118 added `/work run` routing block with no tests; WRK-1053 added scripts with claimed test pass that doesn't cover new code. Route B/C additions must either include tests in execution steps or defer to follow-on WRK with explicit task link.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
