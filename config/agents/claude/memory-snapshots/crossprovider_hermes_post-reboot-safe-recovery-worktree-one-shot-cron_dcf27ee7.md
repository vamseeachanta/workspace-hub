---
name: crossprovider hermes post-reboot-safe-recovery-worktree-one-shot-cron
description: Post-reboot safe recovery: worktree + one-shot cron pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [recovery, cron, git-safety, post-reboot]
---

After reboot with active writers: preserve dirty-work snapshots to `/tmp`, use worktree for reconciliation, create one-shot cron jobs (never recursive) to run deferred cleanup when primary checkout is proven safe (no active writer PIDs), never force-push. Avoids silent state divergence.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
