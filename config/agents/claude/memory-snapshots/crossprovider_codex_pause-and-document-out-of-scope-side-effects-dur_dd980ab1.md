---
name: crossprovider codex pause-and-document-out-of-scope-side-effects-dur
description: Pause and document out-of-scope side effects during WRK execution
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [workflow-discipline, scope-management, work-queue]
---

When executing scoped work on a WRK item, if unrelated files are modified as side effects, pause execution, seek explicit user direction ('continue and document' vs. 'pause and inspect'), and record the decision in the WRK record as 'Out-of-Scope Side Effects'. This prevents scope drift and maintains clarity about actual work boundaries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
