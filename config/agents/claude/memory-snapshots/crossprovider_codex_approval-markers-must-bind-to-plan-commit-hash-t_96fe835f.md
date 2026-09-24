---
name: crossprovider codex approval-markers-must-bind-to-plan-commit-hash-t
description: Approval markers must bind to plan commit hash to detect unreviewed changes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [approval-gates, drift-detection, plan-review]
---

Plan approval that only requires "marker exists" without committing a plan-SHA or comment binding allows undetected plan changes between approval and implementation. Markers should include a reference commit so drift between approved and implemented versions is detectable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
