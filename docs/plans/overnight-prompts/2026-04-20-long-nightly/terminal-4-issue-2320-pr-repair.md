We are in `/mnt/local-analysis/worktrees/workspace-hub-issue-2320` on branch `issue-2320-skill-usage-audit`.

Mission: repair PR #2354 so the implementation for issue #2320 becomes merge-ready tonight. Use the existing branch/worktree; do not widen scope.

Issue: https://github.com/vamseeachanta/workspace-hub/issues/2320
PR: https://github.com/vamseeachanta/workspace-hub/pull/2354
Known failing checks from GitHub right now:
- `Run Tests`
- `Stage Prompt Drift Guard`
- `Review Evidence Check`

Owned paths:
- `scripts/skills/`
- `tests/skills/`
- `docs/reports/skill-invocation-*`
- `docs/plans/README.md`
- `docs/plans/2026-04-17-issue-2320-skill-usage-audit.md` only if execution-time revisions must be documented
- `.nightly-results/2026-04-20-issue-2320.md`

Read-only paths:
- `.github/workflows/`
- `scripts/review/`
- `scripts/quality/`
- PR checks / GitHub Actions logs
- recent git history and issue comments

Forbidden paths:
- `scripts/gtm/`
- `docs/document-intelligence/`
- `tests/gtm/`
- issue surfaces for #2206, #2207, #2209, #2348

Required steps:
1. Re-read PR #2354 checks and fetch the failing run logs with `gh`.
2. Reproduce the failures locally in the smallest possible commands.
3. Fix only what is required to make PR #2354 pass.
4. Run targeted validation locally:
   - the failing test command(s)
   - the local equivalent(s) of stage-prompt-drift / review-evidence checks if available
5. Write `.nightly-results/2026-04-20-issue-2320.md` with:
   - root cause(s)
   - files changed
   - commands run
   - remaining blockers, if any
6. Commit only if validation is green.
7. `git fetch origin --quiet && git rebase origin/main` before push.
8. Push the branch.
9. Post a concise GitHub update on issue #2320 and/or PR #2354 summarizing the repair and evidence.

Execution rules:
- TDD/targeted-repro first; do not blind-edit
- do not rewrite unrelated plan history
- if a failing check is caused by repo-wide infra outside owned paths, document exact evidence, leave the branch otherwise clean, and stop with a blocker report instead of patching unrelated systems
- no user questions
