---
name: crossprovider codex regression-tests-must-be-red-for-intended-reason
description: Regression tests must be RED for intended reason
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [testing, tdd, qa]
---

When adding new contract requirements, the regression suite must fail with expected errors before implementation; RED proves the test exercises the new requirement. A silent pass against old code defeats the regression's purpose and hides incomplete implementations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
