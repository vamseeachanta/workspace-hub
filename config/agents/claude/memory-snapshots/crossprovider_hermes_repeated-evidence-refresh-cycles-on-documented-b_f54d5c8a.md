---
name: crossprovider hermes repeated-evidence-refresh-cycles-on-documented-b
description: Repeated evidence-refresh cycles on documented blockers signal escalation, not progress
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [monitoring-loops, automation-patterns, escalation]
---

Multiple sessions refreshed GitHub labels, git state, and process lists, writing new evidence artifacts each iteration. Each correctly identified the same blockers but couldn't proceed further. When state-refresh doesn't change the documented blocker, continued cycles add no new signal; escalate and summarize instead of iterating.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
