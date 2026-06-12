---
name: crossprovider hermes hermes-claude-code-sync-via-symlinks-not-dual-wr
description: Hermes-Claude Code sync via symlinks, not dual-write
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [architecture, hermes, integration, skills]
---

Architecture: write new skills to ~/.hermes/skills/<category>/<name>/SKILL.md, then create symlink .claude/skills/<category>/<name>/SKILL.md → parent. Single source of truth avoids drift. Hermes external_dirs already configured for .claude/skills/. Applies to skills, scripts, hooks, rules. Symlinks survive git on Linux; Windows support limited.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
