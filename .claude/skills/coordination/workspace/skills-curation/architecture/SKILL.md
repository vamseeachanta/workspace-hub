---
name: skills-curation-architecture
description: 'Sub-skill of skills-curation: Architecture.'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Architecture

## Architecture


Three input pipelines feed a shared output stage:

```
INPUT SOURCES
├── (A) Session candidates    .claude/state/candidates/skill-candidates.md
│       ↓ new candidate signals from previous sessions
├── (B) Knowledge graph       .claude/skills/SKILLS_GRAPH.yaml
│       ↓ skill scores vs active WRK demand
└── (C) Online research       WebSearch
        ↓ new tools, deprecations, patterns in active domains

GAP TRIAGE
├── Shallow gap → auto-create skill stub in .claude/skills/
└── Deep gap    → spin off WRK item (blocked_by:[], plan_approved:false)

OUTPUT LOGGING
├── .claude/state/curation-log.yaml          (run history + cadence)
├── .claude/state/skills-research-log.jsonl  (per-run research results)
└── .claude/state/skills-graph-review-log.jsonl (graph analysis outputs)
```

---
