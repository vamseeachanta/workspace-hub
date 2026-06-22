---
name: crossprovider codex ordinal-ids-are-unsafe-if-derived-from-path-hash
description: Ordinal IDs are unsafe if derived from path, hash, or filesystem traversal order
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [proof-safety, ordinal-ids, reproducibility]
---

Path-derived order varies with symlink resolution; hash-derived order leaks content identity; `rglob()` order is filesystem-dependent and not reproducible across reruns. Safe ordinals need explicit tie-break rules (e.g., by document register line + bucket count) and permutation-invariance tests that shuffle inputs and verify stable output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
