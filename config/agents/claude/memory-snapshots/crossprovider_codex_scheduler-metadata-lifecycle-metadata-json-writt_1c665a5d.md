---
name: crossprovider codex scheduler-metadata-lifecycle-metadata-json-writt
description: Scheduler metadata lifecycle: _metadata.json written post-run only
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scheduler, metadata, async-timing]
---

_metadata.json with format/provenance metadata is scheduler-owned and written by DataScheduler only after successful run completion. Plans and acceptance criteria must account for this timing constraint; tests should verify metadata lands in the correct root alongside output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
