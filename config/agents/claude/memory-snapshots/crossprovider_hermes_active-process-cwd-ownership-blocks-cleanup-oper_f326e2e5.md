---
name: crossprovider hermes active-process-cwd-ownership-blocks-cleanup-oper
description: Active process CWD ownership blocks cleanup operations
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [process-safety, worktree-cleanup]
---

Generated files and worktrees cannot be safely removed when 30+ active processes have their CWD in the repo root. Always verify process ownership (via pgrep) and prove active writers are cleared before cleanup. Stashing/deleting without ownership proof disrupts concurrent sessions.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
