---
name: drillbotics-ace-engineering-gap-vs-drillbotics-requirements
description: 'Sub-skill of drillbotics: ACE Engineering Gap vs Drillbotics Requirements.'
version: 1.1.0
category: engineering/drilling
type: reference
scripts_exempt: true
---

# ACE Engineering Gap vs Drillbotics Requirements

## ACE Engineering Gap vs Drillbotics Requirements


| Module | ACE Status | Priority to Build |
|--------|-----------|-----------------|
| Drilling domain knowledge | ✅ `drilling-expert` agent | — |
| Python sim infrastructure | ✅ `digitalmodel` | — |
| AI orchestration | ✅ workspace-hub | — |
| ROP model | ❌ Missing | **H1** (standalone client value) |
| Wellbore hydraulics | 🟡 Partial (CT-only) | **H1** — generalise `ct_hydraulics.py` |
| Torque and drag | ❌ Missing | **H2** |
| 3D trajectory planner | ❌ Missing | **H2** |
| Drilling controller | ❌ Missing | **H2** |
| Well control / kick detection | ❌ Missing | **H2** |
| Formation classification (ML) | ❌ Missing | **H2** |
| D-WIS semantic layer | ❌ Missing | **H3** |

Full engagement strategy: `docs/strategy/drillbotics-engagement.md`

---
