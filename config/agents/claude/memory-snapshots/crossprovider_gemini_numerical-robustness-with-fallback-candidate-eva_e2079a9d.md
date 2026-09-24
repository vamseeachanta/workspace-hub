---
name: crossprovider gemini numerical-robustness-with-fallback-candidate-eva
description: Numerical robustness with fallback candidate evaluation
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [numerical-algorithms, linear-algebra, mesh-decimation]
---

When solving matrix equations in iterative algorithms (e.g., QEM mesh decimation's optimal contraction), detect singular matrices and fall back to evaluating a candidate set (v1, v2, midpoint) rather than failing. Costs are computed for each candidate; lowest-cost is selected.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
