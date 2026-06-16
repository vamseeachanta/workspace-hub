---
name: crossprovider codex enforcement-guards-with-default-scope-miss-out-o
description: Enforcement guards with default scope miss out-of-scope tracked files at CI time
metadata:
  type: reference
  source: codex
  bridged: 2026-06-15
  tags: [security, enforcement, ci, scope-gap]
---

Security guards like `check-model-id-sourcing.sh` that scan only specific directories (scripts/, config/, agent-library) have a CI masking gap: tracked files outside those paths (.github/workflows/*.yml, etc.) are scanned by CI but not by the guard's default scope, allowing violations to slip through in the enforcement gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
