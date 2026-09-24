---
name: crossprovider codex session-signal-state-is-transient-and-should-def
description: Session-signal state is transient and should defer in cleanup
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [session-state, artifact-lifecycle]
---

`.claude/state/session-signals/` files are generated and consumed by readiness tooling; mark as DEFER unless explicitly issue-scoped. Don't batch transient session state with durable plan artifacts in cleanup commits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
