---
name: crossprovider codex sparse-checkout-does-not-indicate-file-absence
description: Sparse checkout does not indicate file absence
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [git, governance-audit, sparse-checkout]
---

When auditing whether a file exists in a repository, read the canonical blob from `origin/main` (e.g., `git show origin/main:<path>`), not the working tree. Sparse checkouts intentionally omit tracked files; absence in the working copy is not evidence that the file is untracked or gone from the repository.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
