# Exit Handoff — Codex SOUL Drift Checker Parity

**Generated:** 2026-06-02 21:41 America/Chicago  
**Repo:** `workspace-hub`  
**Task:** Close out Codex session workflow parity fix after PR merge.

## Current State

The Codex session workflow parity fix is merged.

- PR: https://github.com/vamseeachanta/workspace-hub/pull/2951
- Merge commit: `9c6c8c7c0ffeac1d2803eb15db2c6ece072b4d50`
- Merged at: `2026-06-03T02:41:18Z`
- Issue comments posted on workspace-hub #2841:
  - https://github.com/vamseeachanta/workspace-hub/issues/2841#issuecomment-4608496582
  - https://github.com/vamseeachanta/workspace-hub/issues/2841#issuecomment-4608588736
  - https://github.com/vamseeachanta/workspace-hub/issues/2841#issuecomment-4608593689

## What Changed

PR #2951 fixed a regression where `scripts/enforcement/check-soul-runtime-drift.sh` rebuilt `config/agents/codex/AGENTS.runtime.md` without the Codex-only skill-index and universal-rules suffix that `scripts/agents/build-soul-runtime.sh` appends. That made the valid Codex runtime surface look drifted.

Merged changes:

- Added `scripts/agents/soul-runtime-lib.sh` as the shared Codex extras helper.
- Updated `scripts/agents/build-soul-runtime.sh` to use the shared helper.
- Updated `scripts/enforcement/check-soul-runtime-drift.sh` to use the same helper when checking `codex/AGENTS.runtime.md`.
- Added regression coverage in `scripts/agents/tests/test_build_soul_runtime_codex.sh`.
- Regenerated `config/agents/codex/AGENTS.runtime.md` from the current skill tree.

## Verification

Verified in the clean PR worktree before merge:

- `bash scripts/agents/tests/test_build_soul_runtime_codex.sh` passed.
- `bash scripts/enforcement/check-soul-runtime-drift.sh` passed.
- `bash scripts/legal/legal-sanity-scan.sh --diff-only --quiet` passed.

GitHub checks on PR #2951 were green before merge. After merge, a new `claude-review` check was observed `IN_PROGRESS`; prior `claude-review`, baseline tests, enforcement gates, and GitGuardian checks were successful.

## Important Correction

The fix was first accidentally committed and pushed to unrelated branch `fix/track-fleet-skills-2925-portable` as `c0fb67b77`.

That accidental branch contamination was corrected:

- Revert commit on that branch: `1ad453c45`
- Scoped clean PR commit: `f40f3de5a`
- Durable merge surface: PR #2951

## Current Workspace Residue

Expected/pre-existing dirty state remains in the primary checkout and was not touched. Examples include provider report JSON/Markdown/HTML files, skill-eval outputs, `.planning/plan-approved/2945.md`, and many untracked memory snapshot files.

Known first-level worktrees observed:

- `/mnt/local-analysis/workspace-hub`
- `/home/vamsee/.config/superpowers/worktrees/workspace-hub/issue-2945-flywheel-closeout`
- `/mnt/local-analysis/wshub-phase0`

Scratch residue observed under `/tmp` includes pre-existing files such as `/tmp/test_fix.py` and `/tmp/wt-vbatch-14/...`; not from this Codex closeout.

## Suggested Skills For Next Session

- `github:github` for PR/issue status checks.
- `github:gh-fix-ci` if the post-merge `claude-review` check fails.
- `coordination/pre-completion-cleanup-audit` before final closeout claims.
- `operations/mnt-analysis-cleanup` only if the next session is explicitly scoped to broader `/mnt/local-analysis` cleanup.

## Next Checkpoint

Check PR #2951 post-merge CI once the new `claude-review` check finishes:

```bash
gh pr view 2951 --repo vamseeachanta/workspace-hub --json state,mergedAt,mergeCommit,statusCheckRollup
```

If it passes, no further action is needed for the Codex SOUL drift checker fix. Do not touch the unrelated dirty primary checkout unless the next task is explicitly about that branch or cleanup.
