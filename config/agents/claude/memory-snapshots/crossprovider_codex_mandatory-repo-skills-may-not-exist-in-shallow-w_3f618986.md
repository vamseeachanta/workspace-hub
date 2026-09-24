---
name: crossprovider codex mandatory-repo-skills-may-not-exist-in-shallow-w
description: Mandatory repo skills may not exist in shallow worktrees; fallback to workspace-hub canonical
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [environment, workflow, workspace-hub]
---

Skills and scripts referenced in repo instructions (e.g., `.claude/skills/coordination/pre-completion-cleanup-audit/SKILL.md`) may be absent from shallow checkouts or isolated worktrees. Fall back to the canonical workspace-hub version or run equivalent checks directly when the local path is unavailable.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
