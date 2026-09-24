---
name: crossprovider gemini session-signals-emit-to-jsonl-for-async-telemetr
description: Session signals emit to JSONL for async telemetry
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [hooks, telemetry, jsonl, signal-architecture]
---

Hook scripts emit one-line JSON records to `.claude/state/session-signals/<signal-type>.jsonl` (e.g., `ai-readiness.jsonl`, `test-health.jsonl`, `session-quality-signals.jsonl`). Each record carries `ts`, `host`, `agent`/`status`/`message` fields. Consumption is async and non-blocking (<1s target); failures are logged but never fatal. This decouples telemetry from session execution.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
