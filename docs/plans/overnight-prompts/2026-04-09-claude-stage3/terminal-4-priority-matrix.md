We are in /mnt/local-analysis/workspace-hub.

Mission:
Create a priority/closure matrix from the 10 stage-2 execution packs.

Write exactly one persisted artifact:
- `docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-4-priority-matrix.md`

Constraints:
1. Claude only.
2. Do NOT mutate GitHub or code.
3. Do NOT ask the user questions.

Required structure:
1. Scoring model (impact, effort, risk, gating friction)
2. Ranked table of all 10 issues
3. Fastest-to-close list
4. Best-to-implement-next list
5. Needs-refinement-first list
6. Final recommended morning order

Verification:
- include all 10 issues
- include explicit numeric or ordinal ranking
- include at least 10 concrete repo references
