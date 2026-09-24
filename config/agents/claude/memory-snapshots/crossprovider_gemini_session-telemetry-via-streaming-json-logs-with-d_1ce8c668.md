---
name: crossprovider gemini session-telemetry-via-streaming-json-logs-with-d
description: Session telemetry via streaming JSON logs with daily rollup
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [instrumentation, session-signals, telemetry, hooks]
---

Capture pre/post tool hooks to a daily JSONL file (one entry per tool call), then process on session stop via emit-session-quality-signals.sh to emit session_tool_summary signals. This approach decouples real-time capture from aggregation, supports active-WRK-item detection, and produces minimal overhead while enabling operational visibility (tool call counts, edit/read ratios per session).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
