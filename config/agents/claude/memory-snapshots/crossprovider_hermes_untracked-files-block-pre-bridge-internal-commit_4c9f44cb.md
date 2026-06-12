---
name: crossprovider hermes untracked-files-block-pre-bridge-internal-commit
description: Untracked files block pre-bridge internal commit; stash recovery is pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflows, memory-management, error-recovery]
---

pre-bridge-quality.sh exits code 1 if untracked files prevent its internal git commit. Recover by: git stash, restore `.claude/memory/` from stash, commit/push memory files only, rerun bridge. Don't manually merge stash.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
