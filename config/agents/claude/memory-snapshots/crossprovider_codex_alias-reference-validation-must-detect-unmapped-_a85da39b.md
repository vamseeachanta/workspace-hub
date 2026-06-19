---
name: crossprovider codex alias-reference-validation-must-detect-unmapped-
description: Alias/reference validation must detect unmapped scope
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [validation, scope-creep, aliasing]
---

Symlink validation that only checks target resolution misses cases where the alias parent contains undeclared siblings. Validation must surface unmapped children counts and constraints rather than silently accepting broad aliases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
