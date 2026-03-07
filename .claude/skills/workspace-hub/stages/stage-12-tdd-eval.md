Stage 12 · TDD / Eval | task_agent | heavy | parallel-optional
Entry: evidence/execute.yaml, WRK-NNN-lifecycle.html#s10
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run full test suite; capture results
2. Map each AC to test result (PASS/FAIL/N/A+reason)
3. Fix any FAIL before writing matrix (no partial passes)
4. Write ac-test-matrix.md via Write tool
5. Update lifecycle HTML Stage 12 section (AC matrix summary)
Exit: ac-test-matrix.md (all ACs: PASS or N/A+reason; no FAIL)
HEAVY CHECK: execute.yaml must have ≥3 integrated_repo_tests entries
