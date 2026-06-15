---
name: crossprovider codex review-artifacts-in-gitignore-require-explicit-f
description: Review artifacts in gitignore require explicit force-add for durability
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git, process, review-workflow]
---

Review output files (e.g., `scripts/review/results/*.md`) ignored by `.gitignore` don't survive handoff or remain visible to future sessions unless explicitly force-added with `git add -f`. Plans relying on review evidence must either force-add artifacts or exclude them from gitignore, or the review trail becomes local-only and lost.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
