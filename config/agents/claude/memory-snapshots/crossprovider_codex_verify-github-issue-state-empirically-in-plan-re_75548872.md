---
name: crossprovider codex verify-github-issue-state-empirically-in-plan-re
description: Verify GitHub issue state empirically in plan reviews
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, github-verification, execution-risk]
---

Plans that reference GitHub issues often assume issue state at plan-write time, but issues can be updated asynchronously before review/execution. Adversarial reviews should verify current state via `gh issue view` or direct inspection rather than trusting plan assumptions, as divergence can silently break gate sequences, acceptance criteria, and dependency relationships.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
