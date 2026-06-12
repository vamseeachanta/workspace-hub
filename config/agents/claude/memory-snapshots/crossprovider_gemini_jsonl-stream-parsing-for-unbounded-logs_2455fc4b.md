---
name: crossprovider gemini jsonl-stream-parsing-for-unbounded-logs
description: JSONL stream parsing for unbounded logs
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [parsing, concurrency, file-handling]
---

Files growing indefinitely (cost-tracking.jsonl, logs) must be parsed line-by-line, never bulk-loaded. Handle json.JSONDecodeError and incomplete lines (concurrent writes can truncate last line). Always open with `encoding='utf-8'` explicit.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
