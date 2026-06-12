---
name: crossprovider hermes run-claude-prompt-sh-budget-usd-flag-incompatibi
description: run-claude-prompt.sh -budget-usd flag incompatibility in nextwave launchers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes-orchestration, shell-scripting, tooling-bug]
---

Script line 11 uses undefined `-budget-usd` flag causing 'command not found' when launching nextwave follow-up sessions; likely version mismatch or missing flag handler in environment. When launcher fails silently, verify script version and compare with active shell invocations.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
