---
name: crossprovider codex label-state-conflicts-signal-missing-user-approv
description: Label state conflicts signal missing user approval
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [github-labels, approval-gates, operational]
---

When an issue has both `status:plan-review` and `status:plan-approved` labels simultaneously, this indicates a label-state conflict, not user approval. Evidence must come from explicit approval comments or issue state, not label presence. A PR merge does not satisfy the user-approval gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
