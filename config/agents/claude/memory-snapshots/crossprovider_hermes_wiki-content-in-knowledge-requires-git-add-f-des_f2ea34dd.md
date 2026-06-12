---
name: crossprovider hermes wiki-content-in-knowledge-requires-git-add-f-des
description: Wiki content in knowledge/ requires git add -f despite .gitignore
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [wiki-management, gitignore, knowledge-persistence]
---

Knowledge pages under `knowledge/wikis/*` are excluded by `.gitignore`; use `git add -f` to track important wiki files. Without force-add, wiki pages remain untracked and disappear on worktree switch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
