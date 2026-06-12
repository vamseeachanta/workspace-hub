---
name: crossprovider hermes wave-based-dispatch-for-large-parallel-session-b
description: Wave-based dispatch for large parallel session batches
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-workflows, batch-dispatch, session-orchestration]
---

For 10+ parallel Claude/agent sessions, partition work into dependency waves, generate unique prompts per wave, and dispatch in dependency order. Avoids cross-session file collisions and allows earlier waves to inform later ones.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
