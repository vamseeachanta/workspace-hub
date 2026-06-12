---
name: crossprovider hermes dirty-main-checkout-blocks-safe-concurrent-chang
description: Dirty main checkout blocks safe concurrent changes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dirty-state, parallelization, git-safety]
---

When workspace-hub main has untracked/modified files from concurrent work, new agents cannot safely stage/land changes without sweep-contamination. Require worktrees or feature branches to isolate concurrent changes; avoid blind staging into dirty main.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
