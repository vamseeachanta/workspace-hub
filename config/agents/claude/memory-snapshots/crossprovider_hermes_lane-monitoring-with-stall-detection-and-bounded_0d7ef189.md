---
name: crossprovider hermes lane-monitoring-with-stall-detection-and-bounded
description: Lane monitoring with stall detection and bounded follow-ups
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [orchestration, lane-management, tmux-patterns]
---

Classify tmux lanes as RUNNING/COMPLETED_WITH_RESULT/BLOCKED/STALLED_NO_OUTPUT; restart stalled lanes if zero output >90min using committed runner. Create ONE bounded follow-up prompt under `generated/` only for non-destructive planning/review/GTM work, never implementation or GitHub mutations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
