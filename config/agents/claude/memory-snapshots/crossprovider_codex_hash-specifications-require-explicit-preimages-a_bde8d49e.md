---
name: crossprovider codex hash-specifications-require-explicit-preimages-a
description: Hash specifications require explicit preimages and golden vectors
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [hashing, determinism, cross-platform-verification, test-specification]
---

Descriptions like 'sorted keys' and 'canonical UTF-8 JSON' are not executable. Hash contract must define: number rendering, Unicode normalization, null/enum encoding, field exclusion (e.g., self-referential hash fields), decimal precision, and include golden test vectors from Linux and Windows. Semantic validation alone cannot verify cross-platform behavior.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
