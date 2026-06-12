---
name: crossprovider hermes acceptance-criteria-must-spell-out-safety-critic
description: Acceptance criteria must spell out safety-critical semantics explicitly
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [acceptance-criteria, test-driven-development, plan-review, distributed-systems]
---

For distributed/cron systems, vague language ('fail closed', 'clean enough') allows implementation drift. Acceptance must enumerate: exact lease mechanism + expiry, no-overlap policy + PID verification sequence, dirty-worktree fail rule, redaction scope, evidence freshness contract.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
