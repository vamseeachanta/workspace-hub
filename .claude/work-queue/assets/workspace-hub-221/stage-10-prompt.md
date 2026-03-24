# Stage 10 Prompt Package — WRK-1075
## Stage: Work Execution
**Invocation:** task_agent
**Weight:** heavy
**Context budget:** 16 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/execute.yaml`

## Entry reads

### assets/WRK-NNN/WRK-NNN-lifecycle.html#s7-s9
```
[entry_reads: assets/WRK-NNN/WRK-NNN-lifecycle.html#s7-s9 — file not found]
```

### assets/WRK-NNN/routing.yaml
```
[entry_reads: assets/WRK-NNN/routing.yaml — file not found]
```

**Blocking condition:** execute.yaml missing or integrated_repo_tests < 3 entries