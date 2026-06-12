---
name: crossprovider hermes sparse-checkout-overlays-hide-content-use-git-ls
description: Sparse-checkout overlays hide content; use git ls-files for visibility
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree, git, sparse-checkout]
---

Worktree and sparse-checkout modes can hide submodule content from Bash globbing. Don't rely on assumption-based checks or `find` output; use `git ls-files` to verify actual tracked surface. (#2455–#2457 discovered missing digitalmodel submodule via sparse visibility.)

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
