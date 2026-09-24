---
name: crossprovider gemini session-handoff-captures-wrk-state-before-exit
description: Session handoff captures WRK state before exit
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [handoff, wrk-lifecycle, session-exit, state-capture]
---

Use `work-document-exit` skill to append a 'Session Handoff' section to the active WRK file before clearing the session. Section captures: status/% complete, work done (linked to acceptance criteria), files modified (raw list), next steps (actionable), optional resume notes. Enables clean hand-offs mid-task without context loss; format is pasteable git add/commit command.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
