---
name: skills-curation-skill-stub-creation-shallow-gaps
description: 'Sub-skill of skills-curation: Skill Stub Creation (Shallow Gaps).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Skill Stub Creation (Shallow Gaps)

## Skill Stub Creation (Shallow Gaps)


For each shallow gap, create a minimal SKILL.md at the correct path:

**Path convention**: `.claude/skills/<category>/<subcategory>/<skill-name>/SKILL.md`

**Stub frontmatter:**

```yaml
---
name: <skill-name>
description: <one-line description from gap signal>
version: 0.1.0
category: <inferred category>
type: skill
trigger: manual
auto_execute: false
stub: true  # marks as incomplete — fill in on first use
created_by: skills-curation
created_at: <ISO timestamp>
source: <session-candidate|graph-review|online-research>
capabilities: []
tools: []
related_skills: []
requires: []
see_also: []
---

# <Skill Name>

> Stub created by skills-curation — expand on first use.
