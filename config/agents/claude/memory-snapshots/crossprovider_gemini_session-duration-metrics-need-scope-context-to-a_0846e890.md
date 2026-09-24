---
name: crossprovider gemini session-duration-metrics-need-scope-context-to-a
description: Session duration metrics need scope context to avoid misattribution
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [session-metrics, measurement-gotcha, duration-interpretation]
---

Claude's 17h 47m WRK-1002 session included concurrent multi-task context (not work-execution-only), making it appear slower than Codex's 55s. Raw wall-clock time is meaningless without `claimed_at` / `completed_at` bounds and task isolation evidence.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
