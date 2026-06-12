---
name: crossprovider codex revision-bound-plan-approvals-require-exact-comm
description: Revision-bound plan approvals require exact commit match
metadata:
  type: reference
  source: codex
  bridged: 2026-05-26
  tags: [plan-revision-drift, approval-gate, compliance]
---

When approval marker specifies commit `7cc1c0b1a`, implementation is unsafe if checked-out worktree is at `21ee7e84c` (different HEAD) or local plan artifact is stale draft/v1 instead of approved version. This is a compliance gate failure, not a code issue—post blocker rather than guess.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
