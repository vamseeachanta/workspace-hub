---
name: crossprovider gemini ci-gate-surfaces-must-be-symmetric-and-bounded
description: CI gate surfaces must be symmetric and bounded
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [ci, linting, scope, asymmetry]
---

Linting root (.) while type-checking src/ creates asymmetric enforcement; auxiliary scripts outside src/ get unexpectedly caught. Gate boundaries matter more than gate breadth; explicitly exclude auxiliary paths (#2459).

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
