---
name: crossprovider codex atomic-revert-rollback-assumptions-fail-on-actua
description: Atomic revert/rollback assumptions fail on actual PR shape; must verify commit topology
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [deployment, rollback, git-operations]
---

Plans assuming a single `git revert <merge-commit>` works need to verify whether the PR lands as one merge commit or 10+ individual file commits. Codex reviews found plans with no rollback procedure or unrealistic rollback assumptions. Rollback strategy must be tested against the actual expected PR topology.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
