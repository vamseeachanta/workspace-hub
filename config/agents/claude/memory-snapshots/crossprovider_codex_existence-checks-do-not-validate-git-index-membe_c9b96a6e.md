---
name: crossprovider codex existence-checks-do-not-validate-git-index-membe
description: Existence checks do not validate git-index membership
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-safety, test-hazards, integration-testing]
---

Path-existence checks (`Path.exists()`) pass on untracked temporary files, so tests against `/tmp` can mask acceptance of untracked repo files. Integration tests must use real git state or explicit `git ls-files` checks before writes to tracked zones.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
