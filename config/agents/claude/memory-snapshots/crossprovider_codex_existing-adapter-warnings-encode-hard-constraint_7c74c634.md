---
name: crossprovider codex existing-adapter-warnings-encode-hard-constraint
description: Existing adapter warnings encode hard constraints, not bugs to fix
metadata:
  type: reference
  source: codex
  bridged: 2026-06-30
  tags: [data-sourcing, requirements, scope-management]
---

If an existing data adapter warns about missing fields (e.g., RRCAdapter noting casing/well-path unavailable from public dumps), that's a scope constraint for new work, not a technical debt item. Plan source matrix around actual public data availability, don't assume fixes are in scope.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
