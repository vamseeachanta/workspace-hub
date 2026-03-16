---
name: claude-reflect-weekly-reflection
description: 'Sub-skill of claude-reflect: Weekly Reflection (+2).'
version: 2.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Weekly Reflection (+2)

## Weekly Reflection


```bash
# Quick weekly review
/reflect --days 7

# Review patterns
cat ~/.claude/state/reflect-state.yaml
```

## Monthly Deep Reflection


```bash
# Full 30-day analysis
/reflect

# Extended with skill creation
/reflect --days 30
```

## Quarterly Review


```bash
# Extended quarterly analysis
/reflect --days 90

# Review all created skills
ls .claude/skills/
```
