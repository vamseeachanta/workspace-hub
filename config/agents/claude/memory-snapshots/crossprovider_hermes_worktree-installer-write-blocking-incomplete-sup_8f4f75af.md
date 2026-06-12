---
name: crossprovider hermes worktree-installer-write-blocking-incomplete-sup
description: Worktree installer write-blocking: incomplete support
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, worktree, installation, blocker]
---

install-hooks.sh writes to .git/hooks/* which fails in worktrees because .git is a file. Hooks can read from git-common-dir once file exists, but the installer cannot create/update that file from a worktree. Worktree support is incomplete without installer fixes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
