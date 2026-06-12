---
name: crossprovider hermes hermes-parallel-first-dispatch-operating-model
description: Hermes parallel-first dispatch operating model
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [hermes, parallelization, workflow-pattern, optimization]
---

For non-trivial work (3+ files, >10 min, planning/review/implementation), classify as single-lane/parallel-readonly/parallel-worktree. Planning & verification use 3-lane parallelization (code intel, tests/failure surface, architecture/risk). Approved implementation uses isolated git worktrees + background agents for durable repo writes, NOT delegate_task sandboxes. Mechanical/repetitive tasks use scripts first. Preserve approval gates; no implementation before plan approval.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
