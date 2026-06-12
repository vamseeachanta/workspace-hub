---
name: crossprovider hermes protected-branch-pr-workflow-for-tier-1-repos
description: Protected branch PR workflow for tier-1 repos
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-workflow, protected-branches, ci-readiness]
---

Direct main push fails on protected branches; use feature branch pattern (e.g., `fix/repo-ci-readiness-20260507`), push to origin, create PR, squash-merge when approved, pull locally, verify clean state at exact merge commit SHA.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
