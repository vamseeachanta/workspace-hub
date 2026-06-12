---
name: crossprovider hermes repo-scoped-hygiene-stage-only-task-owned-change
description: Repo-scoped hygiene: stage only task-owned changes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, hygiene, multi-session]
---

Inspect dirty state before staging; never stage unrelated files. Prevents sweep-contamination where commits pull in parallel-session changes or generated fixture whitespace from full-suite runs.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
