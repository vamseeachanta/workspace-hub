---
name: crossprovider codex verify-git-push-completion-with-git-ls-remote-ne
description: Verify git push completion with git ls-remote, never trust exit codes alone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, reliability, verification]
---

Git push may exit 0 without completing (silent failures on NTFS-FUSE and shared mounts are common). Always verify with `git ls-remote` before assuming push succeeded.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
