---
name: crossprovider gemini defer-intrusive-session-checks-to-post-session-a
description: Defer intrusive session checks to post-session analytics, not session start
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [session-monitoring, non-blocking-checks, batch-analytics]
---

Session drift detection at startup creates interactive friction and blocks normal workflow. Better pattern: non-blocking rule-load at start, then batch analytics post-session on captured logs. Removes friction while still catching violations for trending and feedback.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
