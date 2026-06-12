---
name: crossprovider gemini plans-stuck-in-5-iteration-cycles-usually-have-u
description: Plans stuck in 5+ iteration cycles usually have underspecified semantics, not missing features
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [planning, semantics, iteration]
---

When a plan document iterates repeatedly without converging (e.g., #2289 v1-v9), the blocker is typically ambiguous or missing semantics (timestamp contracts, boundary conditions, precedence) rather than implementation details. Semantic gaps are harder to spot than feature gaps and compound across revisions.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
