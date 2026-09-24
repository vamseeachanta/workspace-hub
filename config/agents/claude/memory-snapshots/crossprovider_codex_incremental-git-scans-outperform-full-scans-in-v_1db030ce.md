---
name: crossprovider codex incremental-git-scans-outperform-full-scans-in-v
description: Incremental git scans outperform full scans in validation hooks
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, performance, hooks, optimization]
---

For non-precommit validation paths (e.g., encoding checks), using `git diff HEAD~1..HEAD` is ~26x faster than `git ls-files` on large repos (7.2s vs 0.27s). Incremental scans work when the set of files to validate can be narrowed to recent changes; use this for all post-commit checks where full-repo scans are unnecessary.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
