# Stage 4 Prompt Package — WRK-1072
## Stage: Plan Draft
**Invocation:** chained_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/WRK-NNN-lifecycle.html`

## Stage Micro-Skill (rules for this stage)
```
Stage 4 · Plan Draft | chained_agent | medium | single-thread
Entry: pending/WRK-NNN.md, evidence/resource-intelligence.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
0. scripts-over-LLM audit (MANDATORY first step): scan every operation in the WRK spec —
   "Will this run again (same WRK, future WRK, or another agent)?" If ≥25% chance of
   recurrence → add a `## Scripts to Create` section listing each script, its
   inputs/outputs, and which phase creates it. Rule: .claude/rules/patterns.md §Scripts.
1. EnterPlanMode for thinking before writing
2. Define ACs (specific, testable)
3. Write pseudocode for key functions (≥3 steps; N/A+reason allowed for pure-doc WRKs)
4. Write test plan (≥3 entries: what|happy/edge/error|expected; N/A+reason allowed)
5. Record plan in lifecycle HTML Stage 4 section
6. Update lifecycle HTML Stage 4 chip to done
Exit: WRK-NNN-lifecycle.html (Stage 4 section present)

```

## Entry reads

### pending/WRK-NNN.md
```
[entry_reads: pending/WRK-NNN.md — file not found]
```

### assets/WRK-NNN/evidence/resource-intelligence.yaml
```
[entry_reads: assets/WRK-NNN/evidence/resource-intelligence.yaml — file not found]
```

## Chained stages (complete in sequence)

### Chained stage 1: Resource Intelligence
Exit artifacts: ['assets/WRK-NNN/evidence/resource-intelligence.yaml']

### Chained stage 2: Triage
Exit artifacts: ['pending/WRK-NNN.md']

**Blocking condition:** lifecycle HTML Stage 4 section absent