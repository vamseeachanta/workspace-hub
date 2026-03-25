# Stage 19 Prompt Package — workspace-hub-1358
## Stage: Close
**Invocation:** task_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `done/WRK-NNN.md`

## Stage Micro-Skill (rules for this stage)
```
[stage micro-skill not found: stage-19-*.md]
```

## Entry reads

### assets/WRK-NNN/evidence/user-review-close.yaml
```
[entry_reads: assets/WRK-NNN/evidence/user-review-close.yaml — file not found]
```

### assets/WRK-NNN/evidence/gate-evidence-summary.yaml
```
[entry_reads: assets/WRK-NNN/evidence/gate-evidence-summary.yaml — file not found]
```

**Blocking condition:** done/WRK-NNN.md missing after close-item.sh; for type:feature, feature-close-check.sh WRK-NNN must exit 0 (enforced in close-item.sh)