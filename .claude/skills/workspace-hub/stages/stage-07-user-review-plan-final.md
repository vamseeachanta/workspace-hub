Stage 7 · User Review — Plan Final | human_interactive | heavy | single-thread
Entry: WRK-NNN-lifecycle.html#s1-s6, evidence/cross-review.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
1. Read cross-review findings; present revisions to human
2. Apply all requested changes to plan
3. Confirm all P1 findings resolved
4. Ask for explicit final approval
5. Write evidence/plan-final-review.yaml via Write tool:
   confirmed_by, confirmed_at, decision: passed
6. Update lifecycle HTML Stage 7 section; flip chip to done
7. Print: GATE PASSED — /checkpoint WRK-NNN → new session → /resume WRK-NNN
Exit: evidence/plan-final-review.yaml (confirmed_by + confirmed_at + decision: passed)
GATE: Stage 8 blocked until gate-check.py confirms plan-final-review.yaml complete
