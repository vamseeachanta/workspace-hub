---
name: skill-creator-skill-discovery
description: 'Sub-skill of skill-creator: Skill Discovery (+2).'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Skill Discovery (+2)

## Skill Discovery


Skills are discovered from:
1. `.claude/skills/` in project directory
2. `~/.claude/skills/` for user-level skills

## Skill Loading


- **Metadata**: Always loaded (name, description)
- **Body**: Loaded when skill is triggered
- **Resources**: Loaded on demand

## Best Practices for Performance


1. Keep SKILL.md focused (under 500 lines ideal)
2. Move large examples to resources/
3. Reference external documentation for comprehensive APIs
4. Use code blocks sparingly--quality over quantity
