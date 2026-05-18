# Stash export-and-drop cleanup

Use this reference when cleaning stale stashes in a shared workspace-hub checkout after remote absorption, bridge/sync cleanup, or worktree closeout.

## Trigger

- `git stash list` contains safety stashes created during remote absorption or pre-bridge/sync cleanup.
- The current branch already matches `origin/<branch>` or the intended remote state.
- The user asks for cleanup/closeout, not implementation.

## Procedure

1. Inventory stashes with date, message, and SHA:
   - `git stash list --date=iso`
   - `git rev-parse stash@{N}` for each stash.
2. Export before dropping:
   - `git stash show -p stash@{N} > <archive>/stash__N-<sha>.patch`
   - `git stash show --stat stash@{N} > <archive>/stash__N-<sha>.stat`
   - `git stash show --name-status stash@{N} > <archive>/stash__N-<sha>.name-status`
   - record `git show --no-patch --format=fuller stash@{N}`.
3. Classify each stash:
   - **Drop** when unique content is already present in `HEAD` or the stash is stale runtime/generated bridge state.
   - **Preserve** when it contains unresolved source edits, user-authored notes, or ambiguous work product.
   - **Export-only then drop** when it is obsolete but should remain recoverable for audit evidence.
4. Move any untracked exported patch artifacts out of the repo into an off-repo preservation directory, e.g. `/mnt/local-analysis/preserved-workspace-hub-cleanup/<date>/stashes/`.
5. Record checksums and line counts for exported patches:
   - `sha256sum <archive>/*.patch`
   - `wc -l <archive>/*.patch`
6. Drop only after export/classification:
   - `git stash drop stash@{N}`
   - Drop from highest/oldest index carefully or re-list between drops because stash indices shift.
7. Verify final state:
   - `git stash list --date=iso` is empty or contains only intentionally preserved entries.
   - `git status --porcelain=v1 --branch` is the expected clean/dirty state.
   - If closeout depends on remote parity: compare `git rev-parse HEAD` with `git ls-remote origin <branch>`.

## Pitfalls

- Do not drop a stash because its message sounds obsolete. Export and inspect first.
- Do not leave exported stash patches under the repo root unless they are intentionally committed artifacts; preserve cleanup evidence outside the repo to keep the worktree clean.
- Do not restore stale bridge/runtime files from a safety stash when current `HEAD` already contains the durable content.
- Remember stash indices shift after each drop; use SHAs in notes and re-run `git stash list` between destructive operations.
