---
name: crossprovider codex ground-plans-in-live-github-state-including-comm
description: Ground plans in live GitHub state, including comments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [issue-analysis, approval-gate, github-workflow]
---

Issue bodies can frame decisions as open while later comments lock them. Always fetch full issue context with `gh issue view --comments` to capture already-decided state before drafting the plan. Plans grounded only in the issue body may re-open decisions that comments already locked.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
