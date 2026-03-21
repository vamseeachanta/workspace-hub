# Stage 10 Prompt Package — WRK-1389
## Stage: Work Execution
**Invocation:** task_agent
**Weight:** heavy
**Context budget:** 16 KB

## Exit artifacts (must exist before calling exit-stage.sh)
  - `assets/WRK-NNN/evidence/execute.yaml`

## Stage Micro-Skill (rules for this stage)
```
Stage 10 · Work Execution | task_agent | heavy | parallel-optional
Entry: routing.yaml, evidence/activation.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
TDD MANDATORY: write failing tests before any implementation code.
Checklist:
0. scripts-over-LLM check (MANDATORY first step): "Does a script exist? Will this recur?"
   If yes → write or call the script; do not inline via LLM prose.
1. EnterPlanMode — plan test and file strategy before any implementation writes
2. Invoke superpowers/test-driven-development skill
3. Write ALL failing tests first (Red); confirm test collection
4. Implement minimum code to pass (Green); no untested code
5. Refactor while tests stay green
6. Parallel-optional: dispatch independent file sets to parallel agents
7. Write evidence/execute.yaml (integrated_repo_tests ≥3, execution_summary)
8. Git commit + push (commit to main; feat|fix|chore(scope): desc)
Coding style:
- Python: snake_case vars/funcs, PascalCase classes | Files: kebab-case
- Max: 200 lines/file, 50 lines/function, 100 chars/line
- Imports: stdlib → third-party → local; no unused imports
- Comments: explain "why" not "what"; no commented-out code
Testing:
- Fix implementation, not tests — tests are the specification
- No mocks — use real implementations; mock only at external API boundaries
- Test data: prefer standard worked examples (API RP, DNV-RP, ISO)
- Naming: test_<what>_<scenario>_<expected_outcome>; Arrange-Act-Assert
Python: `uv run` always; per-repo commands in config/onboarding/repo-map.yaml
Git: commit to main + push; submodules: commit inside first then update pointer
Legal: run scripts/legal/legal-sanity-scan.sh if porting external code; no client identifiers
Exit: evidence/execute.yaml (≥3 test entries all passing)

```

## Entry reads

### assets/WRK-NNN/evidence/plan-final-review.yaml
```
[entry_reads: assets/WRK-NNN/evidence/plan-final-review.yaml — file not found]
```

### assets/WRK-NNN/routing.yaml
```
[entry_reads: assets/WRK-NNN/routing.yaml — file not found]
```

**Blocking condition:** execute.yaml missing or integrated_repo_tests < 3 entries