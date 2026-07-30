---
name: crossprovider codex status-header-must-match-proposed-transition
description: Status header must match proposed transition
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [planning, status, consistency, gates]
---

When a plan proposes a status transition (e.g., draft→plan-review), update the plan's own body header to match the new status, not just external records. Validators that parse plan headers will fail or flag mismatches if the plan body contradicts the proposed transition.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
