---
name: crossprovider codex task-0-dependency-verification-blocks-all-implem
description: Task 0 dependency verification blocks all implementation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [dependency-gating, task-sequencing, proof-handoff]
---

Before Task 1 executes, verify all upstream issues are closed and all required immutable proof handoffs exist as durable artifacts. Parallel session conflicts are real; missing handoffs indicate upstream work is incomplete. Do not bypass this gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
