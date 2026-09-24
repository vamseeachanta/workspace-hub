---
name: crossprovider codex new-instrumentation-not-integrated-into-downstre
description: New instrumentation not integrated into downstream pipeline
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [instrumentation, integration, architectural, observability]
---

Adding data collection to one collection pathway (e.g., Codex logs) without feeding it into the aggregation step (drift-counts.jsonl) leaves the data visible in raw dumps but invisible to downstream analytics and trend reports.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
