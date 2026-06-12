---
name: crossprovider codex session-signal-emission-via-stop-hook-stdin
description: Session signal emission via Stop hook stdin
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [telemetry, hooks, claude-code]
---

Stop hook receives session context as JSON stdin. Extract session_id with jq, emit telemetry JSONL to .claude/state/session-signals/. Allows instrumentation without modifying main prompt or harness. Must complete in <1s.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
