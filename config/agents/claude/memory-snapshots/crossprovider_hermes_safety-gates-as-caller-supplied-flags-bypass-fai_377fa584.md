---
name: crossprovider hermes safety-gates-as-caller-supplied-flags-bypass-fai
description: Safety gates as caller-supplied flags bypass fail-closed enforcement
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [safety-gates, cron-locking]
---

When `--lease-acquired` and `--worktree-clean` are CLI flags (not discovered/enforced by the script), callers can assert them without proof. Result: readiness/gate logic passes even if the actual preconditions (remote lease, clean worktree) were never verified. gates must be enforced by the script itself, not taken on faith from CLI args; otherwise concurrent cron invocations or dirty workspaces slip through.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
