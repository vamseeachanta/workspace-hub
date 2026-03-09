# Stage 9 Prompt Package — WRK-1056
## Stage: Work-Queue Routing
**Invocation:** chained_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/routing.yaml`

## Entry reads

### assets/WRK-NNN/evidence/activation.yaml
```
[entry_reads: assets/WRK-NNN/evidence/activation.yaml — file not found]
```

**Blocking condition:** routing.yaml missing