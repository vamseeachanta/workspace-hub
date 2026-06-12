---
name: crossprovider codex rolling-time-window-heuristic-for-batch-campaign
description: Rolling time-window heuristic for batch campaign detection
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [heuristics, temporal-grouping, data-mining, domain-heuristics]
---

Group historical events by (entity, field) then assign to rolling time windows where all events within window_days form a batch. Effective for detecting drilling campaign batches from sparse well-spud records without explicit labeling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
