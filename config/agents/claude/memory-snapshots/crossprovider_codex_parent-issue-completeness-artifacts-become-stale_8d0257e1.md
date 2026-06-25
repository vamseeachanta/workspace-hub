---
name: crossprovider codex parent-issue-completeness-artifacts-become-stale
description: Parent issue completeness artifacts become stale quickly and need reconciliation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-24
  tags: [issue-tracking, artifact-staleness, blocker-reconciliation]
---

When a parent issue tracks child completion state in a JSON artifact (e.g., a completeness-evidence file listing which child issues are blocked/done), that artifact falls out of sync with GitHub labels as children are implemented. Before starting new work, check whether the parent's blockers are still accurate by comparing the artifact's claimed blockers against the actual GitHub labels and issue state.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
