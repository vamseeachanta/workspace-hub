---
name: crossprovider codex verify-tracked-files-in-ci-workflows-before-depl
description: Verify tracked files in CI workflows before deployment
metadata:
  type: reference
  source: codex
  bridged: 2026-07-02
  tags: [git, ci, workflow-validation]
---

When validating a CI workflow that runs in GitHub Actions, verify all referenced paths are tracked in git, not just present locally. Use `git cat-file -e HEAD:<path>` to check — untracked working-directory files won't exist in the CI environment. This prevents silent CI failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
