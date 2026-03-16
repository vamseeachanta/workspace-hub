---
name: skills-curation-shallow-gap
description: 'Sub-skill of skills-curation: Shallow Gap (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Shallow Gap (+1)

## Shallow Gap


**Definition**: the pattern is known, implementation is straightforward, no domain expertise required, no architectural decisions needed.

**Examples:**
- A utility skill covering a well-documented library or CLI tool
- A workflow pattern that appeared in multiple sessions
- A candidate with high confidence in the session candidates file

**Action**: auto-create skill stub immediately (see Skill Stub Creation below).


## Deep Gap


**Definition**: requires domain expertise, significant research, architectural decisions, or user collaboration to fill properly.

**Examples:**
- A new engineering domain (e.g., subsea flow assurance) with no existing skills
- A multi-tool workflow requiring design choices
- A candidate with low confidence or unclear scope

**Action**: spin off a WRK item:

```yaml
id: WRK-NNN
title: "[domain] skill gap — needs user input"
status: pending
priority: medium
complexity: medium
blocked_by: []
plan_approved: false
plan_reviewed: false
```

WRK body must include:
- Gap description (what capability is missing)
- Demand evidence (WRK refs, commit frequency, session signals)
- Suggested approach (what research or design is needed)
- For User Review section

---
