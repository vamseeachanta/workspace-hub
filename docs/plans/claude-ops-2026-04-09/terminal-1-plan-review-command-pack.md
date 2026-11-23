We are in /mnt/local-analysis/workspace-hub.

Objective:
Produce a ready-to-run GitHub command pack for the top implementation issues #2059, #2063, and #2056.

Read-only inputs:
- docs/plans/claude-followup-2026-04-09/results/issue-2059-execution-pack.md
- docs/plans/claude-followup-2026-04-09/results/issue-2063-execution-pack.md
- docs/plans/claude-followup-2026-04-09/results/issue-2056-execution-pack.md

Output:
- Write exactly one file: docs/plans/claude-ops-2026-04-09/results/plan-review-command-pack.md

Do NOT modify any other repo file.
Do NOT ask questions.
Do NOT run gh commands that mutate issues.

Required contents:
1. exact gh label/comment commands to move each issue to status:plan-review
2. exact gh label/comment commands to move each issue to status:plan-approved after user approval
3. ordering recommendation for applying the commands
4. command safety notes and rollback commands
5. one short morning-operator checklist

Final line must be:
RECOMMENDATION: APPLY AFTER USER CHOOSES APPROVAL ORDER
