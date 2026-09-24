---
name: crossprovider gemini cumulative-statistics-vs-rolling-windows-in-time
description: Cumulative statistics vs rolling windows in time-series anomalies
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [time-series-analysis, anomaly-detection, statistical-methods]
---

Time-series anomaly detection can use cumulative statistics (all historical data up to point i) rather than fixed rolling windows. Cumulative approach allows baseline to evolve gradually; rolling windows isolate recent behavior. Choice depends on whether old data should anchor the baseline.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
