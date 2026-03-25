# Stage 9 Prompt Package — workspace-hub-1404
## Stage: Work-Queue Routing
**Invocation:** chained_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/routing.yaml`

## Stage Micro-Skill (rules for this stage)
```
[stage micro-skill not found: stage-09-*.md]
```

## Entry reads

### assets/WRK-NNN/evidence/activation.yaml
```
[entry_reads: assets/WRK-NNN/evidence/activation.yaml — file not found]
```

## Chained stages (complete in sequence)

### Chained stage 1: Claim / Activation
Exit artifacts: ['assets/WRK-NNN/evidence/claim-evidence.yaml', 'assets/WRK-NNN/evidence/activation.yaml', 'working/WRK-NNN.md']

**Blocking condition:** routing.yaml missing