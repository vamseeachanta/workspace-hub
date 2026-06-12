---
name: crossprovider hermes post-reboot-work-preservation-use-timestamped-sa
description: Post-reboot work preservation: use timestamped salvage directories before operations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [reboot-recovery, git-safety, data-preservation]
---

After system reboots interrupt session work, preserve dirty/uncommitted changes by moving the checkout to a timestamped recovery path (e.g., `/mnt/local-analysis/reboot-salvage-20260427/`) before executing other git operations. Then commit/push via a separate clean worktree to avoid merge races and silent reverts with active processes.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
