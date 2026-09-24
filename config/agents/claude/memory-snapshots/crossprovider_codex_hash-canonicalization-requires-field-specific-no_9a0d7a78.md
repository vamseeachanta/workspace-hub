---
name: crossprovider codex hash-canonicalization-requires-field-specific-no
description: Hash canonicalization requires field-specific normalization
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hash-determinism, canonicalization, cross-machine]
---

Path separators, case, symlink expansion, HOME/repo-root equivalence, and array ordering must be canonicalized per field type before hashing; key-sort alone is insufficient for determinism across machines.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
