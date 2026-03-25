# Stage 4 Prompt Package — workspace-hub-1358
## Stage: Plan Draft
**Invocation:** chained_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/checklist-04.yaml`

## Stage Micro-Skill (rules for this stage)
```
[stage micro-skill not found: stage-04-*.md]
```

## Entry reads

### pending/WRK-NNN.md
```
[entry_reads: pending/WRK-NNN.md — file not found]
```

### assets/WRK-NNN/evidence/resource-intelligence.yaml
```
[entry_reads: assets/WRK-NNN/evidence/resource-intelligence.yaml — file not found]
```

## Chained stages (complete in sequence)

### Chained stage 1: Resource Intelligence
Exit artifacts: ['assets/WRK-NNN/evidence/resource-intelligence.yaml']

### Chained stage 2: Triage
Exit artifacts: ['pending/WRK-NNN.md']

**Blocking condition:** stage 4 checklist evidence absent