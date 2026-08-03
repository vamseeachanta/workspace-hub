---
name: crossprovider codex approval-markers-require-event-verification-not-
description: Approval markers require event verification, not just syntax/path checking
metadata:
  type: reference
  source: codex
  bridged: 2026-07-18
  tags: [governance, approval-gates, event-verification]
---

Markers stored at a path satisfy syntax but don't prove the underlying approval event occurred. Authentication needs to resolve the actor, timestamp, body content, and edit state. Counting a line in a marker file is insufficient—verify the GitHub event or stored context.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
