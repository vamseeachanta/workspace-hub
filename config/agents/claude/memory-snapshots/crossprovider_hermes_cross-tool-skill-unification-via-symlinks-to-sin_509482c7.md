---
name: crossprovider hermes cross-tool-skill-unification-via-symlinks-to-sin
description: Cross-tool skill unification via symlinks to single .claude/skills source
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [skills, cross-agent, unification]
---

Codex `.codex/skills` and Gemini `.gemini/skills` symlink to repo `.claude/skills/`. Hermes config points `external_dirs` to repo `.claude/skills/`. Single source of truth avoids duplication; backfill scripts (`backfill-skills-to-repo.sh`) route local agent skills into tracked repo. Keeps ecosystem synchronized.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
