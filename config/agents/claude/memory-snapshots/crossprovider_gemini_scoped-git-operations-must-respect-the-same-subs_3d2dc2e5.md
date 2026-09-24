---
name: crossprovider gemini scoped-git-operations-must-respect-the-same-subs
description: Scoped git operations must respect the same subset in multi-repo scripts
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git, multi-repo, consistency]
---

When filtering `git diff` to a subset of repos, also scope related operations like `git diff HEAD --name-only` to the same repo pathspec. Asymmetric scoping (e.g., full diff but scoped file list) causes inconsistency and confuses reviewers.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
