---
name: crossprovider codex codex-session-logs-contain-queryable-rate-limit-
description: Codex session logs contain queryable rate-limit metadata
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [codex, quotas, monitoring]
---

`~/.codex/sessions/*.jsonl` stores rate limits under `rate_limits.secondary` with `used_percent` and `resets_at` fields, enabling local quota monitoring without external APIs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
