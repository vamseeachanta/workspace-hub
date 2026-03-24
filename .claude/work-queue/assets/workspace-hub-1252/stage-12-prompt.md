# Stage 12 Prompt Package — WRK-5104
## Stage: TDD / Eval
**Invocation:** task_agent
**Weight:** heavy
**Context budget:** 16 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/ac-test-matrix.md`

## Stage Micro-Skill (rules for this stage)
```
Stage 12 · TDD / Eval | task_agent | heavy | parallel-optional
Entry: evidence/execute.yaml, WRK-NNN-lifecycle.html#s10
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run full test suite; capture results
2. Map each AC to test result (PASS/FAIL/N/A+reason)
3. Fix any FAIL before writing matrix (no partial passes)
4. Write ac-test-matrix.md via Write tool
5. Update lifecycle HTML Stage 12 section (AC matrix summary)
Testing rules:
- Fix implementation, not tests — tests are the specification
- No mocks — use real implementations; mock only at external API boundaries
- 80% coverage target; critical paths require 100%
- Test data: prefer standard worked examples (API RP, DNV-RP, ISO, textbooks)
- Unit tests < 100ms, integration < 5s; no shared state between tests
Python: `uv run` always; per-repo test commands in config/onboarding/repo-map.yaml
Exit: ac-test-matrix.md (all ACs: PASS or N/A+reason; no FAIL)
HEAVY CHECK: execute.yaml must have ≥3 integrated_repo_tests entries

```

## Entry reads

### assets/WRK-NNN/evidence/execute.yaml
```
[entry_reads: assets/WRK-NNN/evidence/execute.yaml — file not found]
```

### assets/WRK-NNN/WRK-NNN-lifecycle.html#s10
```
[entry_reads: assets/WRK-NNN/WRK-NNN-lifecycle.html#s10 — file not found]
```

**Blocking condition:** ac-test-matrix.md missing or any AC in FAIL state