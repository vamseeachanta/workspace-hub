# Stage 14 Prompt Package — WRK-1161
## Stage: Verify Gate Evidence
**Invocation:** task_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/gate-evidence-summary.yaml`

## Stage Micro-Skill (rules for this stage)
```
Stage 14 · Verify Gate Evidence | task_agent | medium | single-thread
Entry: review.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run: uv run --no-project python scripts/work-queue/verify-gate-evidence.py WRK-NNN
2. Fix any FAIL gates before proceeding (do not skip)
3. Re-run until all gates PASS
4. Write evidence/gate-evidence-summary.yaml (all gates: PASS)
5. Update lifecycle HTML Stage 14 section (gate checklist)
Exit: verify-gate-evidence.py exits 0 + evidence/gate-evidence-summary.yaml

```

## Entry reads

### assets/WRK-NNN/review.md
```
[entry_reads: assets/WRK-NNN/review.md — file not found]
```

**Blocking condition:** verify-gate-evidence.py exits non-zero (any gate FAIL)