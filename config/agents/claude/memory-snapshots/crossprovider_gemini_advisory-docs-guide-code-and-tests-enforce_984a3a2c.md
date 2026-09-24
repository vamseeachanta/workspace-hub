---
name: crossprovider gemini advisory-docs-guide-code-and-tests-enforce
description: Advisory docs guide; code and tests enforce
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [documentation, testing, separation-of-concerns]
---

Adapter/reference files (e.g., CODEX.md, GEMINI.md) can be lightweight (≤20 lines) and point to authoritative contracts. Enforcement lives in shared libraries and test fixtures. This separates documentation guidance from actual validation logic.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
