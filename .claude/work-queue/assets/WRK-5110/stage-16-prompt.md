# Stage 16 Prompt Package — WRK-5110
## Stage: Resource Intelligence Update
**Invocation:** task_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/resource-intelligence-update.yaml`

## Stage Micro-Skill (rules for this stage)
```
Stage 16 · Resource Intelligence Update | task_agent | medium | single-thread
Entry: evidence/future-work.yaml, evidence/execute.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Identify ≥3 lessons learned from this WRK execution
2. Note new tools, patterns, or constraints discovered
3. Write evidence/resource-intelligence-update.yaml (lessons[], additions[])
Exit: evidence/resource-intelligence-update.yaml (lessons[] ≥3 entries)

```

## Entry reads

### assets/WRK-NNN/evidence/future-work.yaml
```
[entry_reads: assets/WRK-NNN/evidence/future-work.yaml — file not found]
```

### assets/WRK-NNN/evidence/execute.yaml
```
[entry_reads: assets/WRK-NNN/evidence/execute.yaml — file not found]
```

**Blocking condition:** resource-intelligence-update.yaml missing additions[] and no_additions_rationale