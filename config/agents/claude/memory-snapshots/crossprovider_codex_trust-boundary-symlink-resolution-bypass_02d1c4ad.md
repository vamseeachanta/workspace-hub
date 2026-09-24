---
name: crossprovider codex trust-boundary-symlink-resolution-bypass
description: Trust boundary symlink-resolution bypass
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, trust-boundaries, path-traversal]
---

Trust validators that explicitly reject literal paths (e.g., `tests/fixtures/...`) but accept path-resolution helpers that follow symlinks can be bypassed when a registry entry matches both the symlink reference and the digest of the symlink's resolved target. Path safety must be enforced before resolution, not after.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
