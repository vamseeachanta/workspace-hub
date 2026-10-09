---
name: discipline-refactor-orchestration-architecture
description: 'Sub-skill of discipline-refactor: Orchestration Architecture.'
version: 2.0.0
category: _internal
type: reference
scripts_exempt: true
---

# Orchestration Architecture

## Orchestration Architecture


```
┌─────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR: discipline-refactor skill                    │
│  (Stays lean, delegates all execution)                      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Phase 1       │   │ Phase 2       │   │ Phase 3       │
│ ANALYSIS      │   │ PLANNING      │   │ EXECUTION     │
│ Explore       │   │ Plan          │   │ general-purpose│
│               │   │ + skill-creator│  │ + git-sync-mgr│
└───────────────┘   └───────────────┘   └───────────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ Phase 4: VALIDATION   │
                │ Bash (run tests)      │
                └───────────────────────┘
```

---
