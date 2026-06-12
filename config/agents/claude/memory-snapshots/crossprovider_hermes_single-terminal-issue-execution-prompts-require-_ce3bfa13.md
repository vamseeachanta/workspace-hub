---
name: crossprovider hermes single-terminal-issue-execution-prompts-require-
description: Single-terminal issue-execution prompts require status:plan-approved gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [prompt-design, automation, governance]
---

Autonomous prompts executing issue fixes in a single terminal must check `gh issue view --json labels` for `status:plan-approved` before writing code; block with 'pending approval' if absent. This gate prevents unsanctioned scope expansion and unreviewed implementations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
