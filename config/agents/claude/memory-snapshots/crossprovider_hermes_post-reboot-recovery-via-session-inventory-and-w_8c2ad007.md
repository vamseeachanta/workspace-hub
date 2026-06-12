---
name: crossprovider hermes post-reboot-recovery-via-session-inventory-and-w
description: Post-reboot recovery via session inventory and worktree isolation
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [recovery-patterns, git-workflow, multi-session-safety]
---

After reboot, inventory parallel sessions before mutation. Prefer separate worktrees or fresh clones over parent-checkout edits to avoid contention with active writers. Preserve uncommitted work via snapshot before destructive ops.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
