---
name: crossprovider codex avoid-emitting-mtime-recency-or-activity-buckets
description: Avoid emitting mtime recency or activity buckets in sensitive reports
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-privacy, artifact-schema, llm-wiki-pattern, data-handling]
---

Do not include `latest_mtime_bucket` or similar recency signals in resource inventory artifacts, even when bucketed. This leaks private folder/file activity patterns. Stick to counts, size histograms, extension mix, and digest overlap; if temporal evidence is needed, gate it behind explicit authorization and annotation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
