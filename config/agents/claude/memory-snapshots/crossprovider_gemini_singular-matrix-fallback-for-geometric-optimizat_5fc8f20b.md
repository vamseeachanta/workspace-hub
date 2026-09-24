---
name: crossprovider gemini singular-matrix-fallback-for-geometric-optimizat
description: Singular matrix fallback for geometric optimization
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [numerical-methods, geometric-optimization, fallback-patterns, linear-algebra]
---

When solving linear systems for geometric optimization (e.g., quadric error metrics), if the matrix is singular, evaluate the objective cost at multiple candidate positions (vertices, midpoint, other critical points) and select the minimum-cost result. Avoids hard failures and provides a reasonable approximation.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
