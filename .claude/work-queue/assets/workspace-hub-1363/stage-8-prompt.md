# Stage 8 Prompt Package — workspace-hub-1363
## Stage: Claim / Activation
**Invocation:** chained_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/claim-evidence.yaml`
  - `assets/WRK-NNN/evidence/activation.yaml`
  - `working/WRK-NNN.md`

## Stage Micro-Skill (rules for this stage)
```
[stage micro-skill not found: stage-08-*.md]
```

## Entry reads

### assets/WRK-NNN/evidence/plan-final-review.yaml
```
[entry_reads: assets/WRK-NNN/evidence/plan-final-review.yaml — file not found]
```

## Chained stages (complete in sequence)

### Chained stage 1: Work-Queue Routing
Exit artifacts: ['assets/WRK-NNN/routing.yaml']

**Blocking condition:** claim-evidence.yaml or activation.yaml missing