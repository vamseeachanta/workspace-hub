# 2026-04-29 Fresh Session Exit Prompt

Copy/paste this into a fresh Hermes session after this closeout.

```markdown
We are starting after the 2026-04-29 reboot/token-reset recovery closeout. Treat the prior PR #356 / #357 / #2433 lane as completed unless verification below says otherwise.

## Verified completed lane

1. `worldenergydata` PR #356
   - PR: https://github.com/vamseeachanta/worldenergydata/pull/356
   - Final PR head: `13efb8a877383736c0ad63194346694099df9217`
   - Passing CI run: https://github.com/vamseeachanta/worldenergydata/actions/runs/25137620183
   - Merge commit: `26b9dc511bd01088471f8f257a8919bfc7e3efb1`
   - Merged at: `2026-04-29T23:06:22Z`
   - Expected state: `MERGED`

2. `worldenergydata` #357
   - Issue: https://github.com/vamseeachanta/worldenergydata/issues/357
   - Closeout comment: https://github.com/vamseeachanta/worldenergydata/issues/357#issuecomment-4348155820
   - Expected state: `CLOSED`

3. `workspace-hub` #2433
   - Issue: https://github.com/vamseeachanta/workspace-hub/issues/2433
   - Closeout comment: https://github.com/vamseeachanta/workspace-hub/issues/2433#issuecomment-4348155966
   - Expected state: `CLOSED`
   - Expected labels include `status:done`; `status:blocked` and `status:plan-approved` were removed.

4. Final recovery handoff doc
   - File: `docs/handoffs/2026-04-28-token-reset-finalization.md`
   - Pushed commit: `cf36fe100e039bbe725e1fe240c1e6273ca2c4c8`
   - Commit message: `docs: finalize worldenergydata recovery handoff`

5. Fresh-session exit prompt doc
   - File: `docs/handoffs/2026-04-29-fresh-session-exit-prompt.md`
   - This file was added as a docs-only handoff artifact.

## Worktree constraints

- Do not mutate `/mnt/local-analysis/workspace-hub` primary checkout until its active/generated planning artifacts are reconciled. It was dirty at closeout and should be inspected only unless explicitly cleaning/reconciling.
- Use clean worktrees/clones for new work.
- Keep `ace-linux-1` as the GitHub mutation control plane.
- Do not force-push.
- Use `--body-file` for GitHub comments/issues.

## Verification commands to run first

```bash
git -C /mnt/local-analysis/final-exit-doc-20260429 fetch origin main
git -C /mnt/local-analysis/final-exit-doc-20260429 status --short --branch
git -C /mnt/local-analysis/final-exit-doc-20260429 rev-parse HEAD
git -C /mnt/local-analysis/final-exit-doc-20260429 rev-parse origin/main

git -C /mnt/local-analysis/recovery-finish-20260428/worldenergydata status --short --branch
git -C /mnt/local-analysis/recovery-finish-20260428/worldenergydata rev-parse HEAD
git -C /mnt/local-analysis/recovery-finish-20260428/worldenergydata rev-parse origin/codex/nextwave-20260427-issue-2433

gh pr view 356 --repo vamseeachanta/worldenergydata --json state,mergedAt,mergeCommit,url,headRefOid
gh issue view 357 --repo vamseeachanta/worldenergydata --json state,url
gh issue view 2433 --repo vamseeachanta/workspace-hub --json state,url,labels

git -C /mnt/local-analysis/workspace-hub status --short --branch
```

Expected:
- PR #356: `MERGED`
- worldenergydata #357: `CLOSED`
- workspace-hub #2433: `CLOSED`, includes `status:done`
- handoff worktree clean and equal to `origin/main`
- primary workspace-hub may be dirty; inspect only unless explicitly reconciling.

## Recommended next work order

User preference after reboot recovery:
1. salvage current work first
2. research/restart ongoing work second
3. set off future work third

Next session should:

1. Salvage / reconcile current dirty primary checkout artifacts without destructive cleanup.
   - Inspect `/mnt/local-analysis/workspace-hub` dirty files.
   - Identify active generated GTM/planning artifacts versus stale noise.
   - Use a clean worktree for any commit/push.

2. Continue unresolved workspace-hub dependencies.
   - Run #2139 / #2146 / #2147 before resuming #2152.
   - Run #2521 before completing #2227.
   - Review `status:plan-review` issues #2510 and #2490 only after review evidence is complete.

3. Future work setup.
   - Use isolated worktrees for new overnight/background work.
   - Follow hard gates: issue → resource intel → plan → adversarial review → `status:plan-review` → user approval → `status:plan-approved` → implementation.

## Stop conditions

Stop and ask before:
- deleting or resetting dirty primary workspace-hub artifacts;
- force-pushing;
- closing/approving issues without current evidence;
- mutating external repos from ace-linux-2 without fresh auth verification.
```
