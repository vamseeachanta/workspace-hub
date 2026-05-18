# Cron report push from dirty or stale main

Use this pattern when a scheduled job generates a small, durable report that must be committed to `main`, but the live workspace has pre-existing dirty/untracked state or local `main` is behind `origin/main`.

## Trigger

- Cron/script output is generated successfully.
- Generated artifacts are ignored by `.gitignore` but explicitly requested for archival.
- `git status` shows unrelated dirty/untracked files that must not be staged.
- `git fetch` shows local `main` is behind `origin/main`, making direct push unsafe.

## Pattern

1. Stage only the requested artifacts in the original workspace, using `git add -f` if they are ignored.
2. Commit the narrow report commit locally.
3. Fetch `origin/main` and compare ahead/behind.
4. If local branch is behind or dirty state makes merge risky, create a clean temporary worktree from current `origin/main`:
   ```bash
   tmp=$(mktemp -d /tmp/report-push-XXXXXX)
   git worktree add -b report-push-YYYY-MM-DD "$tmp" origin/main
   ```
5. Cherry-pick the narrow report commit into the temporary worktree:
   ```bash
   git -C "$tmp" cherry-pick <local-report-commit>
   ```
6. Push from the temporary worktree:
   ```bash
   git -C "$tmp" push origin HEAD:main
   ```
7. Verify remote state and artifact presence:
   ```bash
   git fetch origin main
   git log -1 --oneline origin/main
   git ls-tree --name-only origin/main:path/to/report-dir | grep 'report-YYYY-MM-DD'
   ```
8. Remove the temporary worktree and branch after verification:
   ```bash
   git worktree remove "$tmp"
   git branch -D report-push-YYYY-MM-DD
   ```

## Pitfalls

- Do not stage broad dirty state just because the cron task needs a commit.
- Do not merge/rebase a dirty local `main` during cron closeout unless that was explicitly in scope.
- If generated reports are intentionally ignored, `git add -f` is correct for the narrow artifact set.
- Report any remaining dirty state as pre-existing if it was present before the cron task.
