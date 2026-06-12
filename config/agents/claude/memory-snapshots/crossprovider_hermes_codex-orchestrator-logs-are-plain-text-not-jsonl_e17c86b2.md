---
name: crossprovider hermes codex-orchestrator-logs-are-plain-text-not-jsonl
description: Codex orchestrator logs are plain text, not JSONL
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [codex, log-parsing, orchestrator-logs]
---

Codex session outputs in logs/ are plain text (review verdicts + WRK log entries), not structured JSONL like Claude and Hermes. Parsing strategy must account for review verdict normalization (APPROVE/REJECT/COMMENT) and WRK entry extraction; cannot assume field-based structure.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
