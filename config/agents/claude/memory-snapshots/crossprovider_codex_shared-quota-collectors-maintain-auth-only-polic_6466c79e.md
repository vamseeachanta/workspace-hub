---
name: crossprovider codex shared-quota-collectors-maintain-auth-only-polic
description: Shared quota collectors maintain auth-only policy; local wrappers can estimate
metadata:
  type: reference
  source: codex
  bridged: 2026-06-16
  tags: [quota, status-line, policy]
---

`scripts/ai/assessment/` deliberately refuses estimates for centralized quota (returns N/A if unavailable), but per-tool statusline scripts like `.claude/statusline-command.sh` can surface optically-marked estimates locally without violating shared policy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
