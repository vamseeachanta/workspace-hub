# Stage 15 Prompt Package — WRK-5100
## Stage: Future Work Synthesis
**Invocation:** task_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/future-work.yaml`

## Stage Micro-Skill (rules for this stage)
```
Stage 15 · Future Work Synthesis | task_agent | medium | single-thread
Entry: evidence/execute.yaml, review.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Review execution notes and review.md for deferred ideas
2. Capture each as WRK item if not already in queue (use /work add)
3. Write evidence/future-work.yaml (recommendations[] with disposition/status/captured)
4. All spun-off-new items must have captured: true
Exit: evidence/future-work.yaml (all spun-off-new items captured: true)

```

## Entry reads

### assets/WRK-NNN/evidence/execute.yaml
```
[entry_reads: assets/WRK-NNN/evidence/execute.yaml — file not found]
```

### assets/WRK-NNN/review.md
```
[entry_reads: assets/WRK-NNN/review.md — file not found]
```

**Blocking condition:** future-work.yaml missing or spun-off-new items with captured:false