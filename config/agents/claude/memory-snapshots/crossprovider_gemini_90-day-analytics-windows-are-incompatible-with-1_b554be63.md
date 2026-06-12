---
name: crossprovider gemini 90-day-analytics-windows-are-incompatible-with-1
description: 90-day analytics windows are incompatible with 15-day log retention
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [architectural-constraint, analytics, log-retention, recurring-bug]
---

Multiple plans proposed 90-day invocation/usage windows to flag inactive skills or tools, but session logs rotate every 15 days. This causes false-positive demotions for items used 16-90 days ago. Either reduce the window to ≤15 days or implement persistent state files that aggregate counts beyond log rotation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
