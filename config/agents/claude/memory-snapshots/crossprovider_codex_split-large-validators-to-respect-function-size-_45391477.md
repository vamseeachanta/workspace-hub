---
name: crossprovider codex split-large-validators-to-respect-function-size-
description: Split large validators to respect function-size limits
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [code-structure, testing, constraints]
---

When a validator exceeds 50-line limit, split across separate production files instead of forcing it into one. Maintain coherent authorization behavior and test coverage while respecting size constraints (not a blocker, a shape signal).

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
