---
name: crossprovider codex nul-safe-git-batch-operations-require-z-flag-wit
description: NUL-safe git batch operations require -Z flag with fallback
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, data-safety, byte-safety, batch-operations]
---

Use `git cat-file --batch-command -Z` (not just `--batch`) for byte-safe index transport. Requires odd-byte validation tests and fail-closed fallback on parse error to prevent NUL-collision deserialization bugs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
