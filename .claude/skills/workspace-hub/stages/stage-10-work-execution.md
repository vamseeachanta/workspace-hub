Stage 10 · Work Execution | task_agent | heavy | parallel-optional
Entry: WRK-NNN-lifecycle.html#s7-s9, routing.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
TDD MANDATORY: write failing tests before any implementation code.
Checklist:
0. EnterPlanMode — plan test and file strategy before any implementation writes
1. Invoke superpowers/test-driven-development skill
2. Write ALL failing tests first (Red); confirm test collection
3. Implement minimum code to pass (Green); no untested code
4. Refactor while tests stay green
5. Parallel-optional: dispatch independent file sets to parallel agents
6. Write evidence/execute.yaml (integrated_repo_tests ≥3, execution_summary)
7. Update lifecycle HTML Stage 10 section
Exit: evidence/execute.yaml (≥3 test entries all passing)
