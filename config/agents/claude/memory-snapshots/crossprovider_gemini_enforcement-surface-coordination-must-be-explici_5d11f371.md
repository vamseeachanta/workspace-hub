---
name: crossprovider gemini enforcement-surface-coordination-must-be-explici
description: Enforcement Surface Coordination Must Be Explicit
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [enforcement, governance, architecture]
---

When multiple enforcement surfaces exist (pre-commit hooks, CI gates, dashboard, runtime gates), their enforcement levels (advisory, blocking, signal-only) and handoff points must be explicitly defined. Undefined coordination leaves bypass paths and compliance blind spots.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
