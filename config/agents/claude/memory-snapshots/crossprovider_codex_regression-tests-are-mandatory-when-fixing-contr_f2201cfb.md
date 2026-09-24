---
name: crossprovider codex regression-tests-are-mandatory-when-fixing-contr
description: Regression tests are mandatory when fixing control-flow bugs in complex shell scripts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing-practices, regression-tests, tdd]
---

When a bug fix involves reordering guards or control-flow branches (especially in shell), a regression test asserting the specific bug's symptoms should be added. Without it, the same ordering error recurs. Test matrix should cover: item hidden from correct section, item visible in sections it should appear in, and edge cases like --all. Discovered in WRK-1100 Phase 2: logic fix was sound but left untested, making recurrence likely.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
