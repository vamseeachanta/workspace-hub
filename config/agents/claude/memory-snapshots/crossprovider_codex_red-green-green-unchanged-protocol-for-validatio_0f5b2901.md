---
name: crossprovider codex red-green-green-unchanged-protocol-for-validatio
description: RED/GREEN/GREEN-unchanged protocol for validation work
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [tdd, testing, validation, regression-detection]
---

Schema and configuration work uses a three-step validation: RED (test fails on defect), GREEN (test passes after fix), GREEN-unchanged (run same command again to prove no regression). This catches regressions that single-run tests miss. Commits use pathspec to scope only production files; evidence reports are gitignored but document exact commands, proving reproducibility.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
