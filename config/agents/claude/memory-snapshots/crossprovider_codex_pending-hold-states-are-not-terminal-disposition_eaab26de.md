---
name: crossprovider codex pending-hold-states-are-not-terminal-disposition
description: Pending/hold states are not terminal dispositions; they require future action
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [workflow-gate, governance, readiness-matrix]
---

A readiness matrix can show an issue as 'ready' while dependent rows still carry 'hold-for-owner-review' or 'pending' states. These are deferred states, not terminal. Accepting a deferred state as terminal (blocking nothing) creates untracked review work. Gate semantics must distinguish terminal (ingestion allowed/disallowed) from deferred (requires owner approval before terminal).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
