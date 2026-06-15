---
name: crossprovider codex lfs-cache-should-re-hash-cached-binaries-not-tru
description: LFS cache should re-hash cached binaries, not trust filename as hash
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [lfs-verification, cache-integrity, defensive-loading]
---

When using filename-as-hash for LFS object caching, don't trust the filename alone; independently re-hash the cached binary before use to confirm it wasn't corrupted or replaced. SHA-256 the bytes at load time or fail closed on mismatch, even though the filename matched the pointer oid.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
