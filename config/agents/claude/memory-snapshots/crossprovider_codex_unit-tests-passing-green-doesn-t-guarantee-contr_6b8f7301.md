---
name: crossprovider codex unit-tests-passing-green-doesn-t-guarantee-contr
description: Unit tests passing green doesn't guarantee contract enforcement
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [testing, validation, adversarial]
---

A validator test suite can pass while adversarial mutations (negations, contradictions, edge phrasings) expose unhandled bypasses. Complete validation probes require targeted mutations beyond standard test cases, especially for prose-based rules and negation handling.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
