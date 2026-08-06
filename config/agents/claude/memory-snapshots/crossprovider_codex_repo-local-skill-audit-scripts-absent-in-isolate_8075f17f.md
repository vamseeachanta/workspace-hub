---
name: crossprovider codex repo-local-skill-audit-scripts-absent-in-isolate
description: Repo-local skill/audit scripts absent in isolated worktree; check canonical workspace
metadata:
  type: reference
  source: codex
  bridged: 2026-08-05
  tags: [workflow, worktree, tooling]
---

Mandatory lifecycle scripts (cleanup audit, legal scan) reference repo-local paths that may not exist in a worktree. When the expected path doesn't exist, check the canonical workspace root or run equivalent checks directly. Report the fallback explicitly in closeout.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
