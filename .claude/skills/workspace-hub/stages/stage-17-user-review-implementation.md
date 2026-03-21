Stage 17 · User Review — Implementation | human_interactive | heavy | single-thread
Entry: evidence/execute.yaml, GitHub issue (stages 10-16)
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Human reviews GitHub issue and evidence (Stages 10-16 complete)
2. Agent answers questions; applies any requested fixes
3. Confirm all ACs pass; all gates green
4. Ask for explicit approval
5. Write evidence/user-review-close.yaml via Write tool (decision: approved)
6. Print: GATE PASSED — /checkpoint WRK-NNN → new session → /resume WRK-NNN
Exit: evidence/user-review-close.yaml (decision: approved)
GATE: Stage 18 blocked until gate-check.py confirms decision: approved
