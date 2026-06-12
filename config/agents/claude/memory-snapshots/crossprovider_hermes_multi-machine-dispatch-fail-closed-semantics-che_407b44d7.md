---
name: crossprovider hermes multi-machine-dispatch-fail-closed-semantics-che
description: Multi-machine dispatch fail-closed semantics checklist
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [dispatch-safety, multi-machine, operational-requirements]
---

Multi-machine dispatch must fail (not continue degraded) if any of: dirty/ahead/behind worktree on coordinator or target hosts, unpushed commits on dispatch branch, target host unreachable/unavailable, user unauthorized, missing bot-token environment variable, workflow-gate failures (legal scan, tests, review verdict). Each is a blocker, not a warning.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
