---
name: crossprovider codex baseline-test-defects-must-fold-into-plan-scope-
description: Baseline test defects must fold into plan scope, not inherit false-green
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [test-discipline, baseline-defects, review-honesty]
---

When discovering that test suites are non-hermetic (depend on filesystem permissions, live GitHub state, or external condition), incorporate fixing those defects as plan scope rather than claiming a clean baseline. Otherwise reviews inherit false-green results and plan completion is misverified.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
