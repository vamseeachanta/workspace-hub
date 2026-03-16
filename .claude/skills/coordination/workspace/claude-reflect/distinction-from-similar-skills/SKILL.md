---
name: claude-reflect-distinction-from-similar-skills
description: 'Sub-skill of claude-reflect: Distinction from Similar Skills.'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Distinction from Similar Skills

## Distinction from Similar Skills


| Skill | Trigger | Scope | Data Source |
|-------|---------|-------|-------------|
| `skill-learner` | Post-commit | Single repo | Last commit |
| `claude-reflection` | Auto/session | User interactions | Conversation |
| `claude-reflect` | Manual/scheduled | All 26 repos | 30-day git history |
