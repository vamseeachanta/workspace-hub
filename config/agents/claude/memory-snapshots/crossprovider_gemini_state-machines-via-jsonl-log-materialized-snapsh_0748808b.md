---
name: crossprovider gemini state-machines-via-jsonl-log-materialized-snapsh
description: State machines via JSONL log + materialized snapshot
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [state-machines, data-design, event-sourcing]
---

Implement thread/entity state tracking with append-only JSONL event log + periodic atomic snapshot (tmpfile+rename), plus snapshot metadata tracking byte offset and SHA. JSONL is audit trail, snapshot is O(1) hot-path read, metadata detects staleness without re-parsing. Idempotent transition rules gate replay.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
