---
name: crossprovider codex orchestrator-specific-constraints-tool-mode-unav
description: Orchestrator-specific constraints (tool/mode unavailable) need explicit plan callouts and per-provider testing
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [multi-provider, orchestration, testing-strategy]
---

When a tool or mode is unavailable for one orchestrator (e.g., Codex interactive mode via SSH), the plan must name the gap explicitly and test it per provider. Generic mitigations hide the real constraint and make cross-provider runs fragile.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
