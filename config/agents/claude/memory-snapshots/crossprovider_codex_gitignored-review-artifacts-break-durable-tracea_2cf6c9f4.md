---
name: crossprovider codex gitignored-review-artifacts-break-durable-tracea
description: Gitignored review artifacts break durable traceability
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [git, review-workflow, traceability, artifacts]
---

Review result files (e.g., r1/r2 verdicts) placed in gitignored directories are invisible to `git status` and untracked. This breaks review history across sessions. Plans should either force-add these files with `git add -f` or store them in a tracked path to preserve durable review lineage.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
