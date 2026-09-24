---
name: crossprovider codex lfs-cached-binary-re-hashing-for-integrity
description: LFS cached binary re-hashing for integrity
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [lfs-cache, integrity-checking, fail-closed]
---

LFS cache verification should extract the pointer OID, independently re-hash the cached bytes with SHA-256, and fail closed on mismatch rather than trusting filename-as-hash convention alone. This catches corrupted or tampered cache entries.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
