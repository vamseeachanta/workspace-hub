---
name: crossprovider codex blocking-defects-require-exact-reproductions-in-
description: Blocking defects require exact reproductions in matrix form, not examples
metadata:
  type: reference
  source: codex
  bridged: 2026-07-17
  tags: [testing, acceptance-criteria, matrix-verification]
---

"Test the errno cases" is too vague. "Prove `ENOENT → 127`, all other pre-child errors → 126, and cover all exception subclasses" is blockerworthy. Matrix-form test cases (error type × condition grid) catch implementation defects (like subclass dispatch bugs) that linear positive tests miss.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
