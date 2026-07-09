---
name: crossprovider codex scheduler-metadata-format-is-hardcoded-in-base-j
description: Scheduler metadata format is hardcoded in base job writer
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [scheduler-jobs, metadata, gotchas]
---

The generic scheduler job base writer hardcodes `"format": "parquet"` or similar in `_metadata.json`. When adding jobs with different output formats (e.g., CSV), verify actual format or override metadata after writing to avoid mismatches with downstream consumers.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
