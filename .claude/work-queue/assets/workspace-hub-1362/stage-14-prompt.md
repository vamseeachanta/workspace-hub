# Stage 14 Prompt Package — workspace-hub-1362
## Stage: Verify Gate Evidence
**Invocation:** task_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/gate-evidence-summary.yaml`

## Stage Micro-Skill (rules for this stage)
```
[stage micro-skill not found: stage-14-*.md]
```

## Entry reads

### assets/WRK-NNN/review.md
```
[entry_reads: assets/WRK-NNN/review.md — file not found]
```

**Blocking condition:** verify-gate-evidence.py exits non-zero (any gate FAIL)