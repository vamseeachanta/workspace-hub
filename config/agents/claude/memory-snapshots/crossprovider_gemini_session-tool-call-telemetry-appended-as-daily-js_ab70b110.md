---
name: crossprovider gemini session-tool-call-telemetry-appended-as-daily-js
description: Session tool-call telemetry appended as daily JSONL for trend analysis
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [telemetry, session-instrumentation, quality-metrics]
---

.claude/state/session-signals/YYYY-MM-DD.jsonl records {ts, event: session_tool_summary, wrk, tool_calls, edits, reads} at session exit. Append-only design enables trend analysis without database. Counts distinguish Write/Edit/MultiEdit (edits) from Read/Glob/Grep (reads).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
