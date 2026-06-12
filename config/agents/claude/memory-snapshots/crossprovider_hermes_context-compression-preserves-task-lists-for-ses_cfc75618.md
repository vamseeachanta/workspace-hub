---
name: crossprovider hermes context-compression-preserves-task-lists-for-ses
description: Context compression preserves task lists for session continuation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [context-preservation, task-management, long-running-work, hermes]
---

Active task lists using `[>] item. Description. (in_progress)` and `[ ] item. Description. (pending)` format survive context-window compression and guide continuation across multiple handoffs. Enables long-running work to survive without losing progress state across compressed sessions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
