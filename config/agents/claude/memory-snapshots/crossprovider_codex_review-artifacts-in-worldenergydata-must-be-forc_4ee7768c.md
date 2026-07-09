---
name: crossprovider codex review-artifacts-in-worldenergydata-must-be-forc
description: Review artifacts in worldenergydata must be force-added to git
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [git-workflow, planning-process, worldenergydata]
---

Plan review results under `scripts/review/results/` are in `.gitignore` and must be force-added (`git add -f`) to stage them with plan PRs. Without this, review artifacts don't reach GitHub and the plan-review workflow stalls before approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
