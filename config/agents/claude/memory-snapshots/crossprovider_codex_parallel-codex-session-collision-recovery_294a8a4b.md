---
name: crossprovider codex parallel-codex-session-collision-recovery
description: Parallel Codex session collision recovery
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-agent, worktree-safety, process-management]
---

When multiple Codex sessions target the same worktree, identify the older session by PID and stop only that one cleanly — do not race or trample. Preserve all work from the earlier session and let it complete; the user-invoked session takes precedence but must not overwrite live writes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
