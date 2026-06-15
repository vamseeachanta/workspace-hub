---
name: crossprovider codex plan-review-artifacts-require-forced-git-staging
description: Plan review artifacts require forced git staging
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [git-workflow, plan-review, governance]
---

`.gitignore` excludes `scripts/review/results/`, so plan review artifacts don't stage with normal `git add`. Use `git add -f scripts/review/results/2026-*.md` when committing plan reviews to include attested evidence and findings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
