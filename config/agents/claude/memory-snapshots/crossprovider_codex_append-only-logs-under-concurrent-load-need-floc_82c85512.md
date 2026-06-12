---
name: crossprovider codex append-only-logs-under-concurrent-load-need-floc
description: Append-only logs under concurrent load need flock or atomicity
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [concurrency, logging, safety]
---

Multiple concurrent writers appending to the same JSONL log can interleave records and break chaining/integrity guarantees. Use file locking (`flock`) or atomic operations; assume worst-case concurrency (parallel agents, CI runners). Single-threaded or slow-path testing misses races.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
