---
name: crossprovider codex module-size-ceiling-400-lines-triggers-extractio
description: Module size ceiling (400 lines) triggers extraction for security code
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [code-organization, security, refactoring, maintainability]
---

Security-sensitive modules hitting size ceilings should be split by extracting narrowly scoped helpers (descriptor scanning, bound enumeration) rather than bloating core logic. This keeps each security boundary reviewable and testable in isolation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
