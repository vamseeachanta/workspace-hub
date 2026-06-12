---
name: crossprovider codex control-flow-bug-fixes-require-regression-tests-
description: Control-flow bug fixes require regression tests to prevent recurrence
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [regression-testing, control-flow, test-coverage]
---

When a bug is in function logic (early return, off-by-one ordering), lack of automated tests makes recurrence likely across refactors. Even brief matrix tests covering the fixed path (e.g., periodic items in working vs pending sections) lock down expectations and catch regressions quickly.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
