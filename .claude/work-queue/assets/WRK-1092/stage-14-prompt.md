# Stage 14 Prompt Package — WRK-1092
## Stage: Verify Gate Evidence
**Invocation:** task_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/gate-evidence-summary.yaml`

## Entry reads

### assets/WRK-NNN/review.md
```
[entry_reads: assets/WRK-NNN/review.md — file not found]
```

**Blocking condition:** verify-gate-evidence.py exits non-zero (any gate FAIL)