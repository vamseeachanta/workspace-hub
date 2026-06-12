---
name: crossprovider hermes partial-bundle-completion-is-valid-terminal-stat
description: Partial bundle completion is valid terminal state, not failure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [autonomous-work, outcome-classification, multi-issue-bundles]
---

Multi-issue bundles can legitimately end in `blocked_partial` (some issues closed, others blocked by dependencies or approval gates) rather than binary success/failure. Distinguish: `succeeded` (all issues closed), `blocked_partial` (some closed, some blocked with evidence), `failed` (execution error). Report evidence for each outcome class.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
