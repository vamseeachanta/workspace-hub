---
name: crossprovider gemini rolling-window-trend-analysis-bounds-compute
description: Rolling-window trend analysis bounds compute
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [trend-analysis, performance, data-bounding]
---

When detecting patterns from timestamped logs (corrections, session signals), use a bounded rolling window (90 days) rather than all-time analysis. Run full compaction once per quarter. Prevents O(N) scan growth as history accumulates.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
