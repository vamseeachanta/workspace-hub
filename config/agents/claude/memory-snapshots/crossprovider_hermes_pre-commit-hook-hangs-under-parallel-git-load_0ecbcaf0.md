---
name: crossprovider hermes pre-commit-hook-hangs-under-parallel-git-load
description: Pre-commit hook hangs under parallel git load
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git, parallel-load, performance, hook-hang]
---

Workspace-hub under >20 concurrent git processes deadlocks on chained operations (add && commit && push); use atomic per-file calls separated by `;` instead (e.g., `git add -- A; git add -- B; git commit`).

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
