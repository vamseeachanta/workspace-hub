# Stage 20 Prompt Package — WRK-5106
## Stage: Archive
**Invocation:** task_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `archive/WRK-NNN.md`

## Stage Micro-Skill (rules for this stage)
```
Stage 20 · Archive | task_agent | light | single-thread
Entry: done/WRK-NNN.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run: bash scripts/work-queue/archive-item.sh WRK-NNN
2. Verify archive/WRK-NNN.md exists
3. Regenerate INDEX.md
4. Clear active-wrk: bash scripts/work-queue/clear-active-wrk.sh
Git:
- Archive commit format: `chore(WRK-NNN): archive WRK-NNN <title>`
- Commit to main + push immediately
Exit: archive/WRK-NNN.md + updated INDEX.md + active-wrk cleared

```

## Entry reads

### done/WRK-NNN.md
```
[entry_reads: done/WRK-NNN.md — file not found]
```

**Blocking condition:** archive/WRK-NNN.md missing after archive-item.sh