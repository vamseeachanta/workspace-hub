---
name: claude-reflect-with-skill-learner
description: 'Sub-skill of claude-reflect: With skill-learner (+3).'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# With skill-learner (+3)

## With skill-learner


- Shares pattern extraction logic
- Extended for multi-repo analysis
- Complementary triggers (post-commit vs periodic)

## With repo-sync


- Uses parallel git operations
- Leverages submodule enumeration

## With skill-creator


- Invoked when score >= 0.8
- Passes pattern data for skill generation

## State Files Updated


- `~/.claude/state/reflect-state.yaml`: Reflection history
- `~/.claude/state/skills-progress.yaml`: Skill updates
- `.claude/skill-registry.yaml`: New skill entries
