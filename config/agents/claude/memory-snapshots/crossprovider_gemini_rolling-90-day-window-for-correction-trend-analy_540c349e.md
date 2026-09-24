---
name: crossprovider gemini rolling-90-day-window-for-correction-trend-analy
description: Rolling 90-day window for correction trend analysis
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [trend-analysis, performance, data-management]
---

Correction/signal trend analysis uses rolling 90-day window (filter by file modification date) to avoid repeated full scans. Full compaction across all dates runs at most once per quarter; track last compaction date in metadata file to gate re-derivation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
