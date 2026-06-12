---
name: crossprovider hermes git-operations-from-non-root-working-directory-f
description: Git operations from non-root working directory fail silently
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, working-directory, error-handling]
---

Path-based `git rm` or `git add -- <path>` from subdirectories may fail or behave unexpectedly, with minimal error output. Always execute from repo root when issuing pathspec-mode git commands.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
