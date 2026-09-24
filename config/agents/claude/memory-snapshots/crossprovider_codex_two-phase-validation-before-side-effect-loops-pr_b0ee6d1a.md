---
name: crossprovider codex two-phase-validation-before-side-effect-loops-pr
description: Two-phase validation before side-effect loops prevents partial mutations
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-engineering, validation-patterns, fail-closed-design]
---

Scripts that mutate tracked files should validate all targets before writing any single target. Mutations inside per-item loops can leave partial state with no audit trail if late items fail. Enforce an all-or-nothing preflight validation step.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
