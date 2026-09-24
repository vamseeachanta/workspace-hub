---
name: crossprovider codex review-artifacts-are-ignored-and-require-forced-
description: Review artifacts are ignored and require forced staging
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git-workflow, gitignore, staging]
---

Review result files (e.g., `scripts/review/results/*.md`) are typically ignored by `.gitignore` with `!!` rules. Normal `git add` misses them; use `git add -f scripts/review/results/...` to stage. Plans that anticipate this use the `-f` flag; this is a recurring pattern in the review-to-approval workflow.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
