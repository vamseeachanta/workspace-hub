---
name: skill-creator-execution-checklist
description: 'Sub-skill of skill-creator: Execution Checklist.'
version: 2.2.0
category: _internal
type: reference
scripts_exempt: true
---

# Execution Checklist

## Execution Checklist


Before creating a skill:
- [ ] Scope clearly defined (problem, users, inputs, outputs)
- [ ] Name follows kebab-case convention
- [ ] Description is action-oriented with use cases

During creation:
- [ ] Frontmatter complete (name, description, version, category)
- [ ] Overview explains value in 2-3 sentences
- [ ] Quick Start provides immediate value
- [ ] Instructions are actionable, not conceptual
- [ ] Examples are complete and runnable

After creation:
- [ ] Skill triggers correctly when invoked
- [ ] Code examples tested and working
- [ ] Related skills referenced in new skill's frontmatter
- [ ] **Existing related skills updated** — search for skills that overlap or compose with this one; add this skill to their `related_skills:` frontmatter (bidirectional linking is mandatory)
- [ ] Version history added
