# Stage 10 Prompt Package — WRK-1142
## Stage: Work Execution
**Invocation:** task_agent
**Weight:** heavy
**Context budget:** 16 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/execute.yaml`

## Stage Micro-Skill (rules for this stage)
```
Stage 10 · Work Execution | task_agent | heavy | parallel-optional
Entry: WRK-NNN-lifecycle.html#s7-s9, routing.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
TDD MANDATORY: write failing tests before any implementation code.
Checklist:
0. scripts-over-LLM check (MANDATORY first step): before coding any non-trivial operation
   inline, ask "Does a script already exist for this? Will this logic recur?" If yes to
   either → write or call the script; do not inline via LLM prose. Applies to: data
   transforms, file mutations, gate checks, report generation, index rebuilds.
   Rule: .claude/rules/patterns.md §Scripts Over LLM Judgment.
1. EnterPlanMode — plan test and file strategy before any implementation writes
2. Invoke superpowers/test-driven-development skill
3. Write ALL failing tests first (Red); confirm test collection
4. Implement minimum code to pass (Green); no untested code
5. Refactor while tests stay green
6. Parallel-optional: dispatch independent file sets to parallel agents
7. Write evidence/execute.yaml (integrated_repo_tests ≥3, execution_summary)
8. Update lifecycle HTML Stage 10 section
Exit: evidence/execute.yaml (≥3 test entries all passing)

```

## Entry reads

### assets/WRK-NNN/WRK-NNN-lifecycle.html#s7-s9
```
[entry_reads: assets/WRK-NNN/WRK-NNN-lifecycle.html#s7-s9 — file not found]
```

### assets/WRK-NNN/routing.yaml
```
[entry_reads: assets/WRK-NNN/routing.yaml — file not found]
```

**Blocking condition:** execute.yaml missing or integrated_repo_tests < 3 entries