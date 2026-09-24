---
name: crossprovider codex session-metrics-via-jsonl-signals-organized-by-d
description: Session metrics via JSONL signals organized by date
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [metrics, audit-log, jsonl, session-tracking]
---

Store session-level metrics (timestamps, tool counts, active WRK items, cost estimates) in line-delimited JSON files under `.claude/state/session-signals/YYYY-MM-DD.jsonl`. Each line is immutable; append-only design prevents race conditions and simplifies auditing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
