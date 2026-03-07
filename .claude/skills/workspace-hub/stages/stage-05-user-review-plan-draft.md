Stage 5 · User Review — Plan Draft | human_session | heavy | parallel (Route C)
Entry: WRK-NNN-lifecycle.html#s1-s4 (sections 1-4 only)
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Route C: open 3 terminals (Claude/Codex/Gemini) simultaneously; each reviews independently.
Checklist:
1. Open lifecycle HTML; read Plan Draft section (Stage 4)
2. Present each AC / pseudocode block; wait for response before continuing
3. Apply all requested revisions before moving to next section
4. Route C: synthesize 3 provider variants into combined-plan.md
5. Ask for explicit final approval from human
6. Write evidence/user-review-plan-draft.yaml (decision: approved|revise) via Write tool
7. Update lifecycle HTML Stage 5 section; flip chip to done
8. DO NOT proceed until decision: approved confirmed
Exit: evidence/user-review-plan-draft.yaml (decision: approved)
GATE: Stage 6 blocked until gate-check.py confirms decision: approved
