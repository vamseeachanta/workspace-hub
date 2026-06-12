---
name: crossprovider hermes hermes-agent-does-not-automatically-route-native
description: Hermes agent does not automatically route native Claude work
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-agent, execution-routing, session-logging, observability]
---

Native Claude sessions log to `.claude/state/sessions/` and `logs/orchestrator/claude/`, not through Hermes runtime. Hermes can ingest these logs post-hoc, but native Claude does not execute *through* Hermes. Session logging and execution routing are orthogonal. Confirming logs exist ≠ proving Hermes execution.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
