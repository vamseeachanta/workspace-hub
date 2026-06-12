---
name: crossprovider hermes concurrent-agents-block-root-checkout-cleanup-du
description: Concurrent agents block root-checkout cleanup during issue closure
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [git-hygiene, worktree-cleanup, multi-agent-coordination, closure-pattern]
---

When 20+ parallel agent processes have CWD under workspace-hub root, cleanup of dirty files and registered worktrees must wait or use flock serialization. Agents cannot safely stash/remove root dirt while other agents are actively writing. This breaks the intended concurrent cleanup-on-close pattern.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
