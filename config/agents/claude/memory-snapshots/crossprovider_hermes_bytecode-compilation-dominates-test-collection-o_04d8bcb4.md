---
name: crossprovider hermes bytecode-compilation-dominates-test-collection-o
description: Bytecode compilation dominates test collection on large repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pytest-performance, caching, large-repo-optimization]
---

worldenergydata test collection bottleneck is UV bytecode compilation of 14K+ files (~10s), not import recursion. Pre-compilation or bytecode caching could accelerate local dev feedback loops.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
