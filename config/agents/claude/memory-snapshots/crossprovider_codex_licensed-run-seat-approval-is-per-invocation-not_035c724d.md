---
name: crossprovider codex licensed-run-seat-approval-is-per-invocation-not
description: Licensed-run seat approval is per-invocation, not per-queue-request
metadata:
  type: reference
  source: codex
  bridged: 2026-07-15
  tags: [licensed-runs, approval-workflow, dispatch, deckhand]
---

Queue-request approval (state:approved) does not authorize individual run execution. Each licensed run must retain separate owner approval before dispatch. Retry mechanics (e.g., rc 75 contention → delete result JSON) are operational; approval status is not automatically inherited.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
