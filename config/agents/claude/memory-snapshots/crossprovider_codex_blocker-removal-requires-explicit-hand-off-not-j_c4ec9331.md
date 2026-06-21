---
name: crossprovider codex blocker-removal-requires-explicit-hand-off-not-j
description: Blocker removal requires explicit hand-off, not just status change
metadata:
  type: reference
  source: codex
  bridged: 2026-06-20
  tags: [workflow, issue-closure, dependency-tracking]
---

Removing a blocker from a parent issue (e.g., #725) must include explicit migration of blocking work to new concrete child blockers. Do not mark it 'resolved' and leave dependent work orphaned. The contract is: old blocker removed ⟹ new blockers added; old blocker removed AND new blockers missing ⟹ state hazard.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
