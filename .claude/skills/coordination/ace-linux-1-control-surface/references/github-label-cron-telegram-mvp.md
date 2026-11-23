# GitHub-label + cron MVP for Telegram/Hermes multi-machine orchestration

## Pattern

When asked to connect Telegram/Hermes to multiple machines for work execution, prefer this staged architecture before direct chat-to-host command dispatch:

1. GitHub issues are the authoritative queue and audit trail.
2. Labels route work: `machine:<host>`, `agent:<provider>`, and status labels.
3. Each host runs a local cron/scheduler worker and only consumes labels assigned to that host.
4. Workers claim a job before execution using a lock/comment/label contract to prevent duplicate work.
5. Workers post progress and artifacts back to the issue.
6. Telegram/Hermes is the notification, status, and approval surface.
7. Direct Telegram command dispatch is a later, separately approved feature after auth, targeting, lock, audit, rollback, and cost controls are proven.

## Planning sequence

1. Verify reachability and installed state for each machine.
2. Draft shared orchestration contract first: queue labels, claim/lock behavior, dry-run mode, evidence comments, failure handling.
3. Then draft host-specific plans: coordinator/control surface and worker machines.
4. Move plans to `status:plan-review` only after adversarial review.
5. Never self-apply `status:plan-approved`; wait for explicit user approval.
6. Implement shared cron/GitHub contract before host-specific workers.

## Anti-patterns

- Treating Telegram connectivity as execution authorization.
- Launching direct chat-to-shell execution without a queue/lock/audit contract.
- Making worker hosts mutate GitHub broadly before auth and label scope are proven.
- Mixing reachability review with implementation/service/env changes.
- Starting host workers before the shared claim/lock semantics exist.
