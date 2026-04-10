We are in /mnt/local-analysis/workspace-hub.

Mission:
Design the next wave of self-contained Claude prompts based on the 10 stage-2 execution packs. These prompts should be ready for tomorrow after the operator applies any needed labels/edits.

Write exactly one persisted artifact:
- `docs/plans/overnight-prompts/2026-04-09-claude-stage3/results/terminal-5-next-wave-prompts.md`

Constraints:
1. Claude only.
2. Do NOT implement code.
3. Do NOT mutate GitHub.
4. Do NOT ask the user questions.

Required structure:
1. Preconditions by issue
2. 5-8 self-contained Claude prompts for the next execution wave
3. Each prompt must specify allowed write paths and negative write boundaries
4. Include cross-review requirements
5. Include verification commands
6. Final batching recommendation

Verification:
- include at least 5 complete prompts
- prompts must be zero-context and executable later
