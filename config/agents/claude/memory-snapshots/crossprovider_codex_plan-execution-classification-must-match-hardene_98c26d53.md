---
name: crossprovider codex plan-execution-classification-must-match-hardene
description: Plan execution classification must match hardened schema, not narrative
metadata:
  type: reference
  source: codex
  bridged: 2026-08-03
  tags: [planning, gates, schema]
---

Plans must declare execution classification using the exact allowed values—`single-lane`, `parallel-readonly`, or `parallel-worktree`—not narrative like "immediate attempted fleet rollout." The schema gates concurrency contracts, worktree/path ownership, and task ordering. Invalid classification blocks approval.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
