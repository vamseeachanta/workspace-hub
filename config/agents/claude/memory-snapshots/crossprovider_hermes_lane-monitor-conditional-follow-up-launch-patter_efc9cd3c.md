---
name: crossprovider hermes lane-monitor-conditional-follow-up-launch-patter
description: Lane monitor conditional follow-up launch pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [lane-keeper, conditional-launch, monitoring-pattern]
---

Cron monitor classifies tmux lanes (RUNNING/COMPLETED_WITH_RESULT/BLOCKED/STALLED_NO_OUTPUT), restarts failed ones, conditionally launches ONE bounded follow-up per run if prior result suggests safe planning/review/GTM/blocker-collapse work. Never implementation without status:plan-approved + isolated worktree.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
