# Stage 8 Prompt Package — WRK-1081
## Stage: Claim / Activation
**Invocation:** chained_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/claim-evidence.yaml`
  - `assets/WRK-NNN/evidence/activation.yaml`
  - `working/WRK-NNN.md`

## Entry reads

### assets/WRK-NNN/evidence/plan-final-review.yaml
```
[entry_reads: assets/WRK-NNN/evidence/plan-final-review.yaml — file not found]
```

**Blocking condition:** claim-evidence.yaml or activation.yaml missing