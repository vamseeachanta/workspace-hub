We are in /mnt/local-analysis/workspace-hub.

Mission:
Create a stage-2 operator-ready execution pack for GitHub issue #2053, using the existing stage-1 dossier as your primary source. This repo still has no open issues labeled `status:plan-approved`, so this is planning-only. Preserve Codex credits by doing this work on Claude only.

Source dossier:
- docs/plans/overnight-prompts/2026-04-09-10claude/results/terminal-10-concept-selection-matrix.md

Write exactly one persisted artifact:
- docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-10-concept-selection-execution-pack.md

Required behavior:
1. Do NOT ask the user questions.
2. Do NOT implement production code, tests, docs, hooks, or workflows outside your assigned result file.
3. You may inspect the repo freely.
4. If the stage-1 dossier is stale, update the execution pack with the latest repo reality.
5. Use uv run for Python commands if needed.
6. Use /tmp only for scratch.
7. End only after the required result file exists and is complete.

Allowed write target:
- docs/plans/overnight-prompts/2026-04-09-10claude-stage2/results/terminal-10-concept-selection-execution-pack.md

Negative write boundaries:
- Do NOT write to any other repo path.
- Specifically do NOT write to any sibling stage-2 result file.

Required structure in the result file:
1. Title and issue metadata
2. Fresh status check since stage-1 dossier
3. Minimal plan-review packet
4. Issue refinement recommendations
5. Operator command pack with exact draft `gh` commands only
6. Self-contained future implementation prompt for Claude
7. Morning handoff
8. Final recommendation line

Verification before finish:
- include at least 3 concrete repo file paths
- include at least 3 concrete shell commands
- include a clear final recommendation line
