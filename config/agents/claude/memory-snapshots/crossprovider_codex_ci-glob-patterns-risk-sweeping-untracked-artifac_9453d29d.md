---
name: crossprovider codex ci-glob-patterns-risk-sweeping-untracked-artifac
description: CI glob patterns risk sweeping untracked artifacts from adjacent work
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [ci, workflow, artifact-management]
---

When a workflow globs for review artifacts (e.g., `*implementation-62*`), untracked files in the same directory from prior issues (e.g., `*plan-51*`) remain visible to downstream staging commands. Separate review artifact cleanup or use explicit pathspec to prevent accidental contamination of commits.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
