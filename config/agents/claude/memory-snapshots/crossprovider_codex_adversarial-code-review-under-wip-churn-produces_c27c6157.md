---
name: crossprovider codex adversarial-code-review-under-wip-churn-produces
description: Adversarial code review under WIP churn produces stale findings
metadata:
  type: reference
  source: codex
  bridged: 2026-06-17
  tags: [methodology, code-review, process]
---

Uncommitted WIPs can change during review, causing findings to tie to a moving target; re-reading during review drifts the snapshot. Lock the worktree or take a committed checkpoint before adversarial review to ensure findings match the reviewed code.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
