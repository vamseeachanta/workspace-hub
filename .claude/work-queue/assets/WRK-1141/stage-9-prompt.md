# Stage 9 Prompt Package — WRK-1141
## Stage: Work-Queue Routing
**Invocation:** chained_agent
**Weight:** light
**Context budget:** 4 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/routing.yaml`

## Stage Micro-Skill (rules for this stage)
```
Stage 9 · Work-Queue Routing | chained_agent | light | single-thread
Entry: evidence/activation.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Load all required skills (work-queue-workflow, workflow-gatepass, domain skills)
2. Confirm delivery order (P1→P2→P3→P4 or as planned)
3. Write routing.yaml (skills_loaded, stage_sequence_from_here)
4. Update lifecycle HTML Stage 9 section
Exit: routing.yaml (work_queue_skill: loaded, work_wrapper_complete: true)

```

## Entry reads

### assets/WRK-NNN/evidence/activation.yaml
```
[entry_reads: assets/WRK-NNN/evidence/activation.yaml — file not found]
```

## Chained stages (complete in sequence)

### Chained stage 1: Claim / Activation
Exit artifacts: ['assets/WRK-NNN/evidence/claim-evidence.yaml', 'assets/WRK-NNN/evidence/activation.yaml', 'working/WRK-NNN.md']

**Blocking condition:** routing.yaml missing