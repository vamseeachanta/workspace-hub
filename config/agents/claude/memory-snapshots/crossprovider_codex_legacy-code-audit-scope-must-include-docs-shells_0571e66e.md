---
name: crossprovider codex legacy-code-audit-scope-must-include-docs-shells
description: Legacy code audit scope must include docs, shells, and Windows scripts, not just source
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [legacy-code, audit-scope, discovery]
---

Plans enumerating which legacy scripts to deprecate often miss runnable artifacts in docs (code examples), shell invocations, and Windows batch files. Incomplete discovery leaves inconsistent cleanup. Search docs and shell directories alongside source tree.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
