---
name: improve-scope
description: 'Sub-skill of improve: Scope.'
version: 1.4.0
category: workspace-hub
type: reference
scripts_exempt: true
---

# Scope

## Scope


| Target | Syncs via git? | Notes |
|---|---|---|
| Skill + command files | Yes | All users get the skill |
| CLAUDE.md, rules, docs | Yes | Shared improvements |
| `.claude/memory/` | Yes | Shared institutional knowledge |
| `.claude/skills/**/*.md` | Yes | Skill improvements shared |
| `.claude/state/` | No (gitignored) | Per-machine audit trail |
