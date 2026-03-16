---
name: skills-curation-error-handling
description: 'Sub-skill of skills-curation: Error Handling.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


| Error | Action |
|-------|--------|
| `SKILLS_GRAPH.yaml` unreadable | Skip Phase 2; log warning; continue with other phases |
| `skill-candidates.md` missing | Skip Phase 1; log info; continue |
| WebSearch returns no results | Log zero-yield for that target; continue |
| Skill stub creation fails (path conflict) | Log error with path; skip creation; do not overwrite |
| WRK item creation fails | Log error; record as pending manual action in curation-log.yaml |
| curation-log.yaml missing | Create it from stub template; continue |

---
