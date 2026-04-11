# Sync Hermes skills across repo ecosystem

## Goal
Run the most appropriate recent one-time script to propagate Hermes/Claude shared skills across the workspace repo ecosystem safely.

## Current context / assumptions
- Workspace root: `/mnt/workspace-hub`
- Recent candidate scripts inspected:
  - `scripts/propagate-ecosystem.sh`
  - `scripts/operations/compliance/propagate_all_skills.sh`
  - `scripts/skills/sync-knowledge-work-plugins.sh`
- `scripts/propagate-ecosystem.sh` appears to be the best fit for "sync all skills across the repo ecosystem" because it:
  - is newer/currently maintained
  - is ecosystem-wide
  - has a `--skills-only` mode
  - supports `--dry-run`
  - links shared skills/provider adapters across repos instead of bluntly copying from `$HOME/.claude/skills`
- `scripts/operations/compliance/propagate_all_skills.sh` looks older/riskier because it copies from `$HOME/.claude/skills` and installs post-commit hooks.
- `scripts/skills/sync-knowledge-work-plugins.sh` is for importing upstream knowledge-work-plugins into workspace-hub, not for propagating skills to all repos.

## Proposed approach
1. Preview changes with:
   `bash scripts/propagate-ecosystem.sh --skills-only --dry-run --verbose`
2. Review whether any repos are skipped due to local modifications.
3. If preview looks correct, execute:
   `bash scripts/propagate-ecosystem.sh --skills-only --verbose`
4. Optionally run a spot verification across repos if needed.

## Step-by-step plan
1. Run dry-run of `scripts/propagate-ecosystem.sh --skills-only --dry-run --verbose`
2. Summarize what would change
3. If approved, run the real command
4. Report final summary and any skipped repos / modified directories

## Files likely to change
- `*/.claude/skills/guidelines`
- `*/.claude/skills/meta`
- `*/.claude/skills/workflows`
- `*/.claude/skills/.gitignore`
- `*/.codex/skills`
- `*/.gemini/skills`
- Potential git index changes for tracked shared skill dirs

## Validation
- Dry-run output is clean
- Real run exits successfully
- Summary shows expected linked/already-linked/skipped counts
- No unintended hook changes because `--skills-only` avoids hook propagation

## Risks / tradeoffs
- Repos with locally modified shared skill directories may be skipped intentionally
- Script may replace matching local shared-skill directories with links after backup
- Provider adapter links will also be created/updated in repos

## Recommendation
Use `scripts/propagate-ecosystem.sh --skills-only` rather than the older copy-based propagation script.

## Open question
Proceed with the dry-run first, then apply if the preview looks right?