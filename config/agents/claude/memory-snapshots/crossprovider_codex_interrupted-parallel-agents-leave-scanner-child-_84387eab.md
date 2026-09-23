---
name: crossprovider codex interrupted-parallel-agents-leave-scanner-child-
description: Interrupted parallel agents leave scanner child processes alive
metadata:
  type: reference
  source: codex
  bridged: 2026-07-22
  tags: [agents, parallel, process-cleanup]
---

When parallel find/rg scan agents are interrupted, their child processes persist and continue driving workspace I/O load. Agents must trap interrupts and explicitly terminate scanner children to prevent orphaned resource-consuming processes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
