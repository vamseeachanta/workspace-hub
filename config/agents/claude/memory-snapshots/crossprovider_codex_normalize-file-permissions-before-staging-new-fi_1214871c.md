---
name: crossprovider codex normalize-file-permissions-before-staging-new-fi
description: Normalize file permissions before staging new files
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [file-permissions, git-workflow]
---

New files created in worktrees may inherit permissive defaults (executable bit set on docs). Use `chmod 644` before staging to match tracked file permissions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
