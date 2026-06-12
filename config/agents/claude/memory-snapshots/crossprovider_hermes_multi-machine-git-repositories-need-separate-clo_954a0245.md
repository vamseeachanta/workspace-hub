---
name: crossprovider hermes multi-machine-git-repositories-need-separate-clo
description: Multi-machine git repositories need separate clones
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, multi-machine, workspace-hub, architecture]
---

Operating on the same `.git` directory from two machines causes lock contention via index.lock, hooks, background agents, and worktrees. Solution: maintain separate local clones per machine, synchronized only through GitHub push/pull operations—never share `.git` across machines even via NFS.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
