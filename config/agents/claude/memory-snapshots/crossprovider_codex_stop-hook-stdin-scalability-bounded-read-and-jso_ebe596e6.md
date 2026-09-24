---
name: crossprovider codex stop-hook-stdin-scalability-bounded-read-and-jso
description: Stop hook stdin scalability — bounded read and JSONL parsing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hooks, performance, tooling]
---

Stop hooks that slurp full JSONL transcripts as single JSON objects trigger timeouts. Fix: read only a bounded prefix (64 KB), parse as line-delimited JSON records, never interpret the full stream as one JSON object. This reduced `consume-signals.sh` from >10s to 0.03s.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
