---
name: crossprovider codex executable-prerequisites-as-governance-gates
description: Executable prerequisites as governance gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [governance, safety, preflight-checks]
---

Use testable bash predicates (test commands, git submodule verification, disk space checks) rather than documentation-only assumptions. Preconditions that fail hard prevent invalid state from propagating into risky operations.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
