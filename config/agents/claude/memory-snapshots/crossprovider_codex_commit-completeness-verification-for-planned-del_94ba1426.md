---
name: crossprovider codex commit-completeness-verification-for-planned-del
description: Commit completeness verification for planned deliverables
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review-process, git-workflow, test-coverage]
---

When a plan specifies files to change or create (reports, tests, support libraries, configs), verify that all deliverables are tracked before approval. Untracked files hide whether the implementation is reproducible from the committed diff alone — a plan that lands only partial tracked changes can pass local tests while failing reproduction.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
