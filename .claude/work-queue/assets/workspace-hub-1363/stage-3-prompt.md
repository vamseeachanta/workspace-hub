# Stage 3 Prompt Package — workspace-hub-1363
## Stage: Triage
**Invocation:** chained_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `pending/WRK-NNN.md`

## Stage Micro-Skill (rules for this stage)
```
[stage micro-skill not found: stage-03-*.md]
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
Exit artifacts: ['assets/WRK-NNN/evidence/checklist-04.yaml']

**Blocking condition:** pending/WRK-NNN.md missing route/workstations/orchestrator fields