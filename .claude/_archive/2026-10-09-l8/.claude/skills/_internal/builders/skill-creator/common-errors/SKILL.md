---
name: skill-creator-common-errors
description: 'Sub-skill of skill-creator: Common Errors.'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Common Errors

## Common Errors


**Error: Skill not triggering**
- Cause: Description too vague or doesn't match user intent
- Solution: Rewrite description with specific use cases and action verbs

**Error: Skill content too large**
- Cause: Too much content in single SKILL.md
- Solution: Move large examples to resources/ folder, keep SKILL.md under 500 lines

**Error: Circular skill references**
- Cause: Skills reference each other in loops
- Solution: Review related_skills, ensure DAG structure

**Error: Outdated code examples**
- Cause: Dependencies or APIs changed
- Solution: Test examples regularly, update version history
