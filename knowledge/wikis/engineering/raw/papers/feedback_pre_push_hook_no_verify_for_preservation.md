> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-02
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_pre_push_hook_no_verify_for_preservation.md

---
name: workspace-hub pre-push hook + push --no-verify for preservation
description: workspace-hub pre-push runs tier-1 quality gates that block codex-generated branches; Iron Law bans only `commit --no-verify`, push is allowed for preservation-only branch pushes
type: feedback
originSessionId: 73cbf578-6fb3-4436-9a95-06ed471cd8b1
---
workspace-hub's pre-push hook (`[pre-push] New branch — running all tier-1 repo checks`) runs ruff/mypy across all tier-1 sibling repos on every push. Codex-generated branches with quality issues (e.g. `assetutilities` ruff: 473 errors) cause the hook to FAIL and block the push, regardless of whether the branch being pushed is the one with the issues.

**The Iron Law in `.claude/skills/workspace-hub/repo-sync/SKILL.md` bans only `git commit --no-verify`. `git push --no-verify` is explicitly allowed for repo-hygiene/preservation-only contexts:**
> "If the user has approved sensible commands and the goal is repo hygiene/sync rather than validation, `git push --no-verify` may be necessary after verifying local/remote state."

**When --no-verify push is appropriate:**
- Pushing a codex-generated branch to PRESERVE local commits before deleting a worktree (the branch becomes a named ref on origin; nothing merges to main; quality gates apply at PR time, not push time)
- Pushing a preservation tag (`preserved/*`) for orphan-SHA durability
- Pushing a session artifact branch (e.g. `nightly-batch-2-plan-review-...`) to its own remote ref

**When --no-verify push is NOT appropriate:**
- Pushing to `main` directly (always run gates)
- Pushing a feature branch intended for PR (the gates exist to keep PR review meaningful)
- Anything the user hasn't authorized as preservation

Verified on 2026-05-01: 4 codex/10thread-* branches with ruff failures couldn't push without `--no-verify`; with `--no-verify` they landed on origin as named refs. The 1 preservation tag (`preserved/2026-05-01-issue-2408-staging`) also needed `--no-verify`.

**How to apply:** if a `git push` of a non-main branch is rejected by the pre-push hook with tier-1 quality failures, and the goal is preservation (not merge), use `--no-verify`. Document in the operation log that gates were skipped intentionally for preservation. Iron Law is preserved.
