---
name: crossprovider codex streaming-jsonl-parsers-need-prefiltering-to-avo
description: Streaming JSONL parsers need prefiltering to avoid memory exhaustion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [streaming-io, jsonl, memory-efficiency, large-files]
---

When parsing large JSONL files, use a prefilter on raw lines before parsing JSON (e.g., keyword presence check) and a capped heap to limit in-memory candidate count. Never load the whole file. This prevents OOM on multi-GB files and keeps performance linear in result size, not file size.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
