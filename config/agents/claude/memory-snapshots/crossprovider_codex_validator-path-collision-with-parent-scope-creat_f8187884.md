---
name: crossprovider codex validator-path-collision-with-parent-scope-creat
description: Validator path collision with parent scope creates silent masquerading
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, scope-drift, coordination]
---

When a focused validator claims a new path but the parent validator already binds it to a broader issue's scope, the focused validator can silently masquerade as the parent, creating scope drift and approval confusion. Path separation must be explicit in planning and binding to avoid umbrella-to-child delegation failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
