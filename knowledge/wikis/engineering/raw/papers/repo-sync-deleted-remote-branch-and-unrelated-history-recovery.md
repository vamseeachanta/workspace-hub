# Archived Skill: `repo-sync-deleted-remote-branch-and-unrelated-history-recovery`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/repo-sync-deleted-remote-branch-and-unrelated-history-recovery`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/repo-sync-deleted-remote-branch-and-unrelated-history-recovery`
Consolidation date: 2026-04-29

---

---
name: repo-sync-deleted-remote-branch-and-unrelated-history-recovery
description: Recover multi-repo sync failures caused by deleted upstream branches, stale git index locks, and local branches with unrelated history to the remote default branch.
version: 1.0.0
source: learned-from-execution
---

# Repo Sync: Deleted Remote Branch + Unrelated History Recovery

Use this when `./scripts/repository_sync pull all` or equivalent multi-repo sync fails and the failing repos are not simply dirty/diverged. This pattern covers three recurring failure modes seen in workspace-hub subrepos:

1. local branch tracks a remote branch that was deleted
2. a stale `.git/index.lock` blocks checkout/pull
3. local branch history is unrelated to the remote default branch, so `git pull` fails with `refusing to merge unrelated histories`

## Symptoms

### Deleted tracked branch
`git pull` shows:

```text
Your configuration specifies to merge with the ref 'refs/heads/<branch>'
from the remote, but no such ref was fetched.
```

### Stale lock
```text
fatal: Unable to create '.git/index.lock': File exists.
```

### Unrelated histories
```text
fatal: refusing to merge unrelated histories
```

## Workflow

### 1. Diagnose the failing repo precisely
For each failed repo:

```bash
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo none
git status --short
git remote -v
git fetch --prune origin
```

Also inspect remote default branch if needed:

```bash
git remote show origin | sed -n '/HEAD branch/s/.*: //p'
git branch -r
```

### 2. If the tracked remote branch was deleted
Do not keep retrying `git pull` on the stale branch.

Recovery:

```bash
git fetch --prune origin
git checkout <default-branch>
git branch --set-upstream-to=origin/<default-branch> <default-branch>
git pull --no-rebase origin <default-branch>
```

Notes:
- In the observed case, `chore/gitignore-claude-worktrees` had been deleted remotely in multiple repos.
- `main` already existed locally and was the correct recovery target.
- After `fetch --prune`, the stale remote-tracking branch disappeared and normal pull succeeded.

### 3. If a stale `.git/index.lock` blocks the fix
Before removing the lock, verify no active git process is operating in that repo.

```bash
ps -ef | grep '[g]it'
```

If the lock is stale, remove it and retry:

```bash
rm .git/index.lock
git fetch --prune origin
git checkout <default-branch>
git branch --set-upstream-to=origin/<default-branch> <default-branch>
git pull --no-rebase origin <default-branch>
```

### 4. If local branch has unrelated history to remote default branch
Do not merge unrelated histories during sync. Preserve local work first, then align to the remote default branch cleanly.

Recovery:

```bash
git fetch --prune origin
git branch preserve/pre-sync-$(date +%Y%m%d) <local-branch>
git checkout -B <remote-default-branch> origin/<remote-default-branch>
git branch --set-upstream-to=origin/<remote-default-branch> <remote-default-branch>
git pull --no-rebase origin <remote-default-branch>
```

Notes:
- This preserves the old local history for later review instead of destroying it.
- In the observed case, local `main` was unrelated to `origin/master`, so the safe fix was:
  - preserve local `main`
  - switch to a clean local `master` tracking `origin/master`
- Do not use `--allow-unrelated-histories` for repo hygiene sync.

### 5. Re-verify repo and ecosystem state
Per repo:

```bash
git status --short --branch
```

Across workspace:

```bash
./scripts/repository_sync status all
```

Success means each repo reports:
- correct tracked branch
- no local changes
- up to date with remote

## Important caveat: root workspace-hub may still be dirty while subrepos are clean
`repository_sync status all` reflects the subrepos it manages. It can report all repos clean/up to date while the workspace-hub root repo is still changing due to active review/background processes.

So after syncing subrepos, separately check the root repo:

```bash
git -C /mnt/local-analysis/workspace-hub status --short --branch
ps -ef | grep -E '[c]odex|[g]emini|[c]laude'
```

If active processes are still writing artifacts, root cleanliness is not stable yet. Commit only what is appropriate, and expect additional follow-up commits until those processes finish.

## Do not
- do not force-push
- do not merge unrelated histories just to make pull succeed
- do not delete old local history without preserving it on a backup branch
- do not remove `.git/index.lock` without first checking for active git processes
- do not declare the whole workspace clean based only on subrepo status if the root repo is still being mutated by running jobs
