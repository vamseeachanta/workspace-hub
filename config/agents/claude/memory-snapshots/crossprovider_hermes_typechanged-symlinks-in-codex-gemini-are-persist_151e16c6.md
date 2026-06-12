---
name: crossprovider hermes typechanged-symlinks-in-codex-gemini-are-persist
description: Typechanged symlinks in .codex/.gemini are persistent state
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [worktree-state, symlink-management, skill-initialization]
---

Sessions show `.codex/skills` and `.gemini/skills` with typechanged status across multiple worktrees; not treated as blocker but appears repeatedly in git status. May indicate configuration sync or skill-symlink initialization issue under multi-agent scenarios.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
