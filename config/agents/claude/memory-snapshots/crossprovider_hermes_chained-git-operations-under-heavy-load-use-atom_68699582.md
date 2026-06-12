---
name: crossprovider hermes chained-git-operations-under-heavy-load-use-atom
description: Chained git operations under heavy load use atomic per-file calls, not && chains
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-concurrency, heavy-load, chained-ops]
---

Under heavy parallel git load (>20 concurrent git processes), chained commands like `git add && git commit && git push` are hazardous; one stalled step kills the chain. Use atomic per-file calls separated by `;` instead. Workspace-hub under autofeed/cron load regularly hits 10+ zombie git-status processes blocking commits.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
