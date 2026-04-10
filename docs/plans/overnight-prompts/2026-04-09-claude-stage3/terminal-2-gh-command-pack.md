We are in /mnt/local-analysis/workspace-hub.

Mission:
Read all 10 stage-2 execution packs under `docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/` and extract a unified draft `gh` command pack for the operator.

Write exactly one persisted artifact:
- `docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-2-gh-command-pack.md`

Constraints:
1. Claude only.
2. Do NOT execute any `gh` command.
3. Do NOT mutate GitHub or production code.
4. Do NOT ask the user questions.
5. Use /tmp only for scratch.

Required structure:
1. Safety notes
2. Commands grouped by issue
3. Commands grouped by action type (comment, edit, label, close, follow-up create)
4. Batch order recommendation
5. Copy/paste blocks with exact commands only
6. Final operator checklist

Verification:
- include commands for as many issues as possible from the packs
- include at least 20 concrete shell commands
- clearly mark all commands as DRAFT ONLY
