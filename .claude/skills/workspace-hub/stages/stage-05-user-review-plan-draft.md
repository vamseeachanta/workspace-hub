Stage 5 · User Review — Plan Draft | human_interactive | heavy | parallel (Route B/C)
Entry: evidence/checklist-04.yaml, GitHub issue (stages 1-4 sections)
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.

Route A (simple): Single-agent interactive planning.
  1. Open GitHub issue in browser; present Plan Draft section
  2. Walk each AC / pseudocode block section-by-section; wait for response before continuing
  3. Apply all requested revisions before moving to next section
  4. Ask for explicit final approval from human — silence is not approval
  5. Write evidence/user-review-plan-draft.yaml (decision: approved|revise) via Write tool
  6. DO NOT proceed until decision: approved confirmed

Route B/C (medium/complex): 3-agent interactive planning + interactive synthesis.
  1. Claude produces initial draft (specs/wrk/WRK-NNN/plan.md); opens GitHub issue
  2. Dispatch Codex and Gemini in parallel using the batch script:
       bash scripts/work-queue/stage5-plan-dispatch.sh WRK-NNN
     Script runs both providers as background processes and waits for both to complete.
     Outputs: plan_codex.md / plan_gemini.md in assets/WRK-NNN/
  3. SYNTHESIS (interactive with user — do NOT auto-merge):
     - Read all 3 plans; build diff table: topic | Claude | Codex | Gemini | recommended
     - Present conflicts section-by-section; wait for user decision on each
     - Write merged sections only after user approves each conflict resolution
     - Write final specs/wrk/WRK-NNN/plan.md from resolved sections
  4. Ask for explicit final approval from human
  5. Write evidence/user-review-plan-draft.yaml (decision: approved|revise) via Write tool
  6. DO NOT proceed until decision: approved confirmed

Exit: evidence/user-review-plan-draft.yaml (decision: approved)
GATE: Stage 6 blocked until gate-check.py confirms decision: approved
