# Stage 2 Prompt Package — WRK-1141
## Stage: Resource Intelligence
**Invocation:** task_agent
**Weight:** medium
**Context budget:** 8 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/resource-intelligence.yaml`

## Stage Micro-Skill (rules for this stage)
```
Stage 2 · Resource Intelligence | chained_agent | medium | single-thread
Entry: pending/WRK-NNN.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Research domain — identify existing infra, skills, constraints
2. Assess complexity (simple/medium/complex)
3. Write evidence/resource-intelligence.yaml (completion_status, domain, skills.core_used ≥3)
4. Update lifecycle HTML Stage 2 section
Exit: evidence/resource-intelligence.yaml

```

## Entry reads

### pending/WRK-NNN.md
```
[entry_reads: pending/WRK-NNN.md — file not found]
```

**Blocking condition:** resource-intelligence.yaml missing completion_status or skills.core_used