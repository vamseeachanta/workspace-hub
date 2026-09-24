---
name: crossprovider codex audit-tools-without-explicit-context-params-sile
description: Audit tools without explicit context params silently misclassify
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [audit-tools, silent-failure, machine-equivalence]
---

Audit and guard tools that omit explicit context params (e.g., --machine) fail silently to resolve current context, leading to misclassification of duplicates and regressions. Always require explicit machine/host resolution when context matters to correctness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
