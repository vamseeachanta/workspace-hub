---
name: crossprovider hermes untracked-files-invisible-in-git-diff-reviews
description: Untracked files invisible in git diff reviews
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, tdd, review-process]
---

git diff excludes untracked files by default. When reviewing TDD diffs, a plan may show new test files that are not yet staged. Verify git status shows tests as tracked before approving, or the actual commit will silently omit them and break TDD coverage.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
