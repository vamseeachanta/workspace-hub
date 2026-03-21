Stage 12 · TDD / Eval | task_agent | heavy | parallel-optional
Entry: evidence/execute.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Run full test suite; capture results
2. Map each AC to test result (PASS/FAIL/N/A+reason)
3. Fix any FAIL before writing matrix (no partial passes)
4. Write ac-test-matrix.md via Write tool
Testing rules:
- Fix implementation, not tests — tests are the specification
- No mocks — use real implementations; mock only at external API boundaries
- 80% coverage target; critical paths require 100%
- Test data: prefer standard worked examples (API RP, DNV-RP, ISO, textbooks)
- Unit tests < 100ms, integration < 5s; no shared state between tests
Python: `uv run` always; per-repo test commands in config/onboarding/repo-map.yaml
Exit: ac-test-matrix.md (all ACs: PASS or N/A+reason; no FAIL)
HEAVY CHECK: execute.yaml must have ≥3 integrated_repo_tests entries
