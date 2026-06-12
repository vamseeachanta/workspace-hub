---
name: crossprovider hermes protected-branch-direct-push-exceptions-are-repo
description: Protected-branch direct-push exceptions are repo-specific and tracked
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, protected-branches, github-api]
---

Most repos require PR for `main` merges, but assetutilities, llm-wiki, and digitalmodel have accepted direct pushes to `main` for specific commits (approval-state, structure-checker). Exception tracking prevents blind retry failures; verify current repo rules before attempting direct push.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
