---
name: crossprovider codex same-filesystem-checks-must-inspect-gitdir-not-r
description: Same-filesystem checks must inspect gitdir, not repo root
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, worktree, path-traversal]
---

When source uses gitfile or worktree, `.git` may not be a real directory under the repo root. Hardlink viability and isolation are determined by the actual `.git/objects` device, not the result of `git rev-parse --show-toplevel`. Check device for the object store, not the toplevel.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
