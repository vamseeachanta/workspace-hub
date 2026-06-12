---
name: crossprovider hermes new-files-silently-excluded-by-gitignore-git-inf
description: New files silently excluded by .gitignore/.git/info/exclude
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-status, exclusion, gitignore, debugging]
---

Written files don't appear in git status if .gitignore or .git/info/exclude prevents them; git status shows no change. Use `git check-ignore <path>` to diagnose exclusion.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
