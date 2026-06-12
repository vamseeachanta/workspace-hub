---
name: crossprovider codex verification-gates-must-be-first-class-plan-step
description: Verification gates must be first-class plan steps with explicit checks
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan, verification, gates, testing]
---

WRK-209 uv enforcement plan lacked post-change validation; verification (grep assertions, bash -n, smoke tests, boundary checks) was missing as a sequenced phase. Plans should enumerate mandatory verification matrix upfront: what will be checked, by which commands, and pass/fail criteria; this prevents silent regressions and enables checkpoints for human review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
