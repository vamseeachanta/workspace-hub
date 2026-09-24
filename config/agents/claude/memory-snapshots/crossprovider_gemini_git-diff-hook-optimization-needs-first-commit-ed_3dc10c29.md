---
name: crossprovider gemini git-diff-hook-optimization-needs-first-commit-ed
description: Git diff hook optimization needs first-commit edge case handling
metadata:
  type: reference
  source: gemini
  bridged: 2026-09-23
  tags: [git, performance, hooks]
---

`git diff HEAD~1..HEAD` achieves 26× performance improvement over `git ls-files` but fails when HEAD~1 doesn't exist. Always handle first-commit and shallow-clone edge cases when optimizing git-based hooks.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
