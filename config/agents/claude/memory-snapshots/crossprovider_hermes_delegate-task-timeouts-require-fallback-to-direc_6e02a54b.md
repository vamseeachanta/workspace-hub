---
name: crossprovider hermes delegate-task-timeouts-require-fallback-to-direc
description: delegate_task timeouts require fallback to direct background agents on large repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [claude-code, workspace-hub, parallel-execution, tooling-quirk]
---

For parallel work on workspace-hub (33K files), delegate_task times out and returns no useful worker summaries. Fallback pattern: use direct `claude` background processes (e.g., `claude -p <path> --no-browser -- <prompt> > .log &`). This is a workspace-hub-specific quirk; plan parallel execution with fallback path ready (don't assume delegate_task succeeds).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
