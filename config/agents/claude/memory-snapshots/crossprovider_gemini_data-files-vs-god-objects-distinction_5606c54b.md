---
name: crossprovider gemini data-files-vs-god-objects-distinction
description: DATA files vs God Objects distinction
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [code-review, refactoring-heuristic, architecture]
---

Files containing ≥95% raw dict records (no logic) are data artifacts, not God Objects. Skip refactoring them; they serve a different role than class-based modules. Use line count and logic density to distinguish.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
