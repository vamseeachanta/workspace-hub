---
name: crossprovider hermes test-portability-git-ls-files-dependency-is-expe
description: Test portability: git ls-files dependency is expected in CI context
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, test-design]
---

Tests using `git ls-files` fail in `git archive` snapshots but work in normal clones/CI environments. Not a merge blocker if CI has .git metadata; note as portability trade-off in test documentation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
