Stage 4 · Plan Draft | chained_agent | medium | single-thread
Entry: pending/WRK-NNN.md, evidence/resource-intelligence.yaml
IMPORTANT: Write evidence files via Write tool only — never Bash echo/sed/cat.
Checklist:
0. scripts-over-LLM audit (MANDATORY first step): scan every operation in the WRK spec —
   "Will this run again (same WRK, future WRK, or another agent)?" If ≥25% chance of
   recurrence → add a `## Scripts to Create` section listing each script, its
   inputs/outputs, and which phase creates it.
1. EnterPlanMode for thinking before writing
2. Define ACs (specific, testable)
3. Write pseudocode for key functions (≥3 steps; N/A+reason allowed for pure-doc WRKs)
4. Write test plan (≥3 entries: what|happy/edge/error|expected; N/A+reason allowed)
5. Check chunk sizing: read config/work-queue/chunk-sizing.yaml — if ANY limit exceeded,
   create a Feature WRK (type: feature) instead of a regular WRK
6. Research before building: check for official API before building scrapers or estimators
Exit: evidence/checklist-04.yaml + plan spec in specs/modules/
