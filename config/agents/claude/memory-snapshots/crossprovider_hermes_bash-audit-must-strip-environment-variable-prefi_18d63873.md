---
name: crossprovider hermes bash-audit-must-strip-environment-variable-prefi
description: Bash audit must strip environment-variable prefixes before command classification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit-tooling, bash-parsing, log-normalization]
---

Variable assignments (WT=..., SKIP_PUSH=..., etc.) prefix bash commands in logs and pollute command-family extraction. Strip leading VAR= patterns before parsing; classify bare assignments as skipped, not commands. Fixes audit-report noise from environment-wrapped invocations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
