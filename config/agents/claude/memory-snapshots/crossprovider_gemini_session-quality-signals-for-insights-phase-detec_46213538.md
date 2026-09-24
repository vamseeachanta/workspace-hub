---
name: crossprovider gemini session-quality-signals-for-insights-phase-detec
description: Session quality signals for insights phase detection
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [quality-metrics, learning-pipeline, signal-detection]
---

Four key quality issues detectable during phase 1 insights: context pollution (≥3 unrelated WRK without `/clear`), skipped planning (≥3 file edits without plan mode invocation), agent loops (tool+file pair ≥5× consecutive), task overload (>15 tool calls before first commit). Requires session-signal emitter to log these events.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
