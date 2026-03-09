Stage 13 · Agent Cross-Review | task_agent | medium | parallel — 3 providers
Entry: WRK-NNN-lifecycle.html#s10-s12, ac-test-matrix.md
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Mandatory: ALL 3 providers (Claude + Codex + Gemini). Same override rule as Stage 6.
Checklist:
0. EnterPlanMode — analyze all implementation + tests before recording any verdict
1. Send implementation + tests to Codex and Gemini simultaneously
2. Each provider reviews: security, correctness, missing ACs, code quality
3. Collect verdicts (APPROVE|REVISE) with P1/P2 findings
4. Write review.md via Write tool (verdict, reviewers[], findings)
5. Update lifecycle HTML Stage 13 section
Exit: review.md (verdict: APPROVE|REVISE; all 3 providers listed)
