---
name: crossprovider codex self-referential-manifest-hashing-is-mathematica
description: Self-referential manifest hashing is mathematically impossible
metadata:
  type: reference
  source: codex
  bridged: 2026-07-14
  tags: [verification, cryptography, architecture]
---

When a legal/scan manifest must enumerate SHA256 hashes of all deliverables including itself, the manifest hash cannot be computed before the list is finalized, yet the list is incomplete without its own hash. Solution: use an immutable scan receipt separate from the manifest, or bootstrap-exclude the manifest from the hash requirement while freezing all other artifacts.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
