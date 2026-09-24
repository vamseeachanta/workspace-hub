---
name: crossprovider codex sparse-worktree-mode-avoids-materializing-large-
description: Sparse worktree mode avoids materializing large corpus on 49K+ file trees
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-optimization, sparse-checkout, large-repos, performance]
---

Use sparse-index checkout with exact path filters to avoid materializing unrelated files (e.g., standards corpus) when targeting only plan or documentation paths. Trades slightly slower index write for orders-of-magnitude reduction in checkout size and faster operations on large repos.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
