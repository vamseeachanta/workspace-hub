---
name: crossprovider codex shared-symlinks-in-multi-agent-environments-need
description: Shared symlinks in multi-agent environments need explicit lifecycle coordination
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-agent, shared-state, lifecycle-management]
---

When multiple agents share a resource (e.g., a symlinked `.venv`), cleanup from one agent can break others mid-operation. Shared state requires coordination: either designate a single cleanup agent or explicitly forbid certain agents from mutating shared state. Fire-and-forget deletion of shared resources is an operational hazard.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
