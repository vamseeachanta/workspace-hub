---
name: crossprovider codex jsonl-for-durable-session-signal-logging
description: JSONL for durable session signal logging
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [logging, jsonl, session-signals, observability]
---

Append structured logs to a `.jsonl` file (one record per line) with ISO 8601 timestamps, hostname, agent name, and status. This enables downstream parsing, grep-ability, and statistical analysis without external dependencies. Pattern: emit on both success and warnings; use consistent fields (ts, host, agent, status, version, message).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
