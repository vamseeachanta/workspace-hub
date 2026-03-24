# Stage 18 Prompt Package — WRK-1183
## Stage: Reclaim
**Invocation:** task_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/reclaim.yaml`

## Stage Micro-Skill (rules for this stage)
```
Stage 18 · Reclaim | task_agent | light | single-thread
Entry: evidence/user-review-close.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Check for assets/WRK-NNN/checkpoint.yaml
2. If no checkpoint: write evidence/reclaim.yaml (status: n/a) via Write tool
3. If checkpoint found: re-orient from checkpoint; write reclaim.yaml (status: reclaimed)
4. Update lifecycle HTML Stage 18 section
Exit: evidence/reclaim.yaml (status: n/a | reclaimed)

```

## Entry reads

### assets/WRK-NNN/evidence/user-review-close.yaml
```
[entry_reads: assets/WRK-NNN/evidence/user-review-close.yaml — file not found]
```

**Blocking condition:** reclaim.yaml missing