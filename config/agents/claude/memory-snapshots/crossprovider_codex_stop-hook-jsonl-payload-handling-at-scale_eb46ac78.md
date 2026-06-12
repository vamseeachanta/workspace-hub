---
name: crossprovider codex stop-hook-jsonl-payload-handling-at-scale
description: Stop-hook JSONL payload handling at scale
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [hooks, jsonl, stdin-handling, performance]
---

Stop hooks that slurp full transcripts as single JSON cause timeout and filename corruption with multi-MB payloads. Use bounded prefix reads + line-by-line JSONL parsing (one record per line, no concatenation). Verified: 14.5 MB transcript processes in 0.03s with bounded reads vs 10s+ timeout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
