---
name: crossprovider hermes multi-repo-isolation-commit-in-place-no-cross-re
description: Multi-repo isolation: commit in place, no cross-repo commits
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [multi-repo, git-operations, isolation]
---

When work spans multiple repos (workspace-hub + digitalmodel + llm-wiki), use separate git checkouts per repo. Commit changes in the repo where they land; do not cross-repo commits. This avoids lock contention and simplifies rollback.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
