# Stage 3 Prompt Package — WRK-5107
## Stage: Triage
**Invocation:** chained_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `pending/WRK-NNN.md`

## Stage Micro-Skill (rules for this stage)
```
Stage 3 · Triage | chained_agent | light | single-thread
Entry: evidence/resource-intelligence.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Read resource-intelligence.yaml
2. Confirm route (A/B/C), workstations, orchestrator
3. Surface open questions; update WRK frontmatter
4. Update lifecycle HTML Stage 3 section
Exit: pending/WRK-NNN.md (route/workstations set)

```

## Entry reads

### assets/WRK-NNN/evidence/resource-intelligence.yaml
```
[entry_reads: assets/WRK-NNN/evidence/resource-intelligence.yaml — file not found]
```

## Chained stages (complete in sequence)

### Chained stage 1: Resource Intelligence
Exit artifacts: ['assets/WRK-NNN/evidence/resource-intelligence.yaml']

### Chained stage 2: Plan Draft
Exit artifacts: ['assets/WRK-NNN/WRK-NNN-lifecycle.html']

**Blocking condition:** pending/WRK-NNN.md missing route/workstations/orchestrator fields