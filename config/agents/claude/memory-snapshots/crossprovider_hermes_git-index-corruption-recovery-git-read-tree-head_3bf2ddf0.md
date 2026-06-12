---
name: crossprovider hermes git-index-corruption-recovery-git-read-tree-head
description: Git index corruption recovery: git read-tree HEAD
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-repair, index-corruption, error-handling]
---

Corrupt .git/index (file smaller than expected) causes git pull to fail silently. Recovery: run `git read-tree HEAD` to rebuild from HEAD tree, or `rm .git/index && git reset`. gsd-researcher script has git_heal_index() function defined (unused) and duplicated inline in bash -c blocks. Pattern should be extracted and reused across scripts.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
