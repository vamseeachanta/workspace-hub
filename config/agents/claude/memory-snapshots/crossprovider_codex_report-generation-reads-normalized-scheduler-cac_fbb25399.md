---
name: crossprovider codex report-generation-reads-normalized-scheduler-cac
description: Report generation reads normalized scheduler cache, not raw sources
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [data-pipeline, reports, scheduler]
---

When building reports over scheduler outputs, read from normalized CSV cache and `_metadata.json` sidecar, not raw source downloads. This leverages the refresh cycle, avoids side effects, and maintains authoritative timestamps. Scheduler caches live under `data/<country>/...` with normalized/ subdirectory.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
