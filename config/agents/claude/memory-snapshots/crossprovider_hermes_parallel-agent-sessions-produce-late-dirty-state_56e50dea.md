---
name: crossprovider hermes parallel-agent-sessions-produce-late-dirty-state
description: Parallel agent sessions produce late dirty-state requiring pre-commit classification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [parallel-agents, git-state, multi-session]
---

Concurrent Hermes sessions can generate uncommitted changes after final pushes (config, tests, scripts, signal logs). Exit closure should not automatically stage these; next session must classify late arrivals before committing to avoid mixing orthogonal work.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
