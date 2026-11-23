We are in /mnt/local-analysis/workspace-hub.

Mission:
Read all 10 stage-2 execution packs under `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/` and produce one concise morning operator runbook.

Write exactly one persisted artifact:
- `docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-1-operator-runbook.md`

Constraints:
1. Claude only.
2. Do NOT mutate GitHub or production code.
3. Do NOT ask the user questions.
4. You may inspect the repo freely.
5. Use /tmp only for scratch.
6. End only after the required result file exists.

Required structure:
1. Executive summary
2. 10-issue table with issue, recommendation, fastest next action, blocker
3. Morning sequence in strict order (first 10 actions)
4. High-risk items vs quick wins
5. Exact file paths to consult for each issue
6. Final recommendation block

Verification:
- include all 10 issues
- include at least 10 concrete repo file paths
- include at least 5 concrete shell commands
