---
name: crossprovider codex batch-verification-test-plan-red-alignment-not-j
description: Batch verification: test-plan RED alignment, not just happy-path
metadata:
  type: reference
  source: codex
  bridged: 2026-06-23
  tags: [testing, batch-workflow, verification]
---

When reviewing batch implementations, verify tests cover plan-required RED/edge-case checks (marker collision, prior-batch regression, untracked-file rejection). Missing RED coverage is a major defect even if artifacts and happy-path tests pass.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
