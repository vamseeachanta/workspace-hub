---
name: crossprovider codex git-plumbing-fallback-for-porcelain-commit-timeo
description: Git plumbing fallback for porcelain commit timeout
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [git-plumbing, commit-tree, timeout-fallback]
---

When `git commit` times out in hooks, use `git commit-tree` + `git update-ref` to bypass porcelain overhead. Document the workaround in issue comment. The resulting commit is normal Git; push works normally afterward.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
