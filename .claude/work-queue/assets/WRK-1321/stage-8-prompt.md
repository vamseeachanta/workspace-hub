# Stage 8 Prompt Package — WRK-1321
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
Stage 8 · Claim / Activation | chained_agent | light | single-thread
Entry: evidence/plan-final-review.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Read agent-quota-latest.json; assess proceed/pause
2. Write evidence/claim-evidence.yaml (quota snapshot, proceed decision)
3. Update working/WRK-NNN.md (status: working, activated_at)
4. Write evidence/activation.yaml (activated_at, gates_confirmed)
Exit: evidence/claim-evidence.yaml + evidence/activation.yaml + working/WRK-NNN.md

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