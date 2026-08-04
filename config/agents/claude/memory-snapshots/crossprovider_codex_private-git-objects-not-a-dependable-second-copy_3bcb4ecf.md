---
name: crossprovider codex private-git-objects-not-a-dependable-second-copy
description: Private git objects not a dependable second copy
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [git-ops, data-safety, backup]
---

After force-push, git objects retrievable via GitHub API but unreferenced by any branch are eligible for garbage collection. 'Retrievable via API' does not mean 'safely preserved'.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
