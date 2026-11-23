# Large Repo Partial Checkout Recovery

Use this when `repository_sync` or `git pull` times out in a very large repo and leaves the branch/ref partly updated, sparse checkout enabled, or thousands of generated/untracked files in the worktree.

## Symptoms

- `git pull --no-rebase` repeatedly times out while `Updating files` or `Updating index flags` for hundreds of thousands of paths.
- Normal `git status` or `git status --porcelain -uall` hangs because generated/untracked trees are huge.
- `HEAD` may equal `origin/main`, but `git status` shows many tracked deletions from directories moved aside during recovery (for example `.claude/...`, `.codex/...`, `.gemini/...`).
- `repository_sync` can leave a long-running `git status --porcelain` process and `.git/index.lock`.

## Fast, Low-Risk Probes

Prefer status commands that do not enumerate untracked files:

```bash
git -c status.showUntrackedFiles=no status --short --branch
git rev-parse HEAD origin/main
git rev-list --left-right --count HEAD...origin/main
git config --get core.sparseCheckout || true
sed -n '1,40p' .git/info/sparse-checkout 2>/dev/null || true
```

Check for hung processes before removing locks:

```bash
ps -eo pid,ppid,stat,etime,cmd | grep -E 'git|repository_sync' | grep -v grep || true
[ -f .git/index.lock ] && stat -c 'LOCK %n size=%s mtime=%y' .git/index.lock
```

If only stale/hung sync/status processes exist, kill them and remove the lock:

```bash
kill <git-status-pid> <repository_sync-pid> 2>/dev/null || true
sleep 2
[ -f .git/index.lock ] && rm -f .git/index.lock
```

## Recovery Pattern

1. Stop hung `repository_sync` / `git status --porcelain` processes and clear only stale `.git/index.lock` after verifying no active git operation remains.
2. If full checkout/pull is too slow, enable sparse checkout deliberately and avoid broad untracked scans.
3. If you must move bulky generated directories aside, preserve them under `.git/recovery-backups/` (inside `.git` so they do not appear as untracked files):

```bash
mkdir -p .git/recovery-backups
for d in .claude.partial-pull-backup-* .codex.partial-pull-backup-* .gemini.partial-pull-backup-*; do
  [ -e "$d" ] || continue
  mv "$d" ".git/recovery-backups/$d"
done
```

4. Restore accidental tracked-file edits/deletions rather than committing them:

```bash
git restore -- <path>
git reset --mixed -q HEAD
git sparse-checkout reapply
```

5. Verify with no-untracked status first, then use bounded untracked summaries only if needed:

```bash
git -c status.showUntrackedFiles=no status --short --branch
git rev-list --left-right --count HEAD...origin/main
git status --porcelain=v1 -uall | awk '{print $1, $2}' | sed 's#\([^ ]*\) \([^/]*\).*#\1 \2#' | sort | uniq -c | sort -nr | sed -n '1,80p'
```

## Do Not Commit Recovery Artifacts

When the user asks to "commit untracked files and push," distinguish real project work from recovery/partial-checkout artifacts. Do not commit `.claude.partial-pull-backup-*`, `.codex.partial-pull-backup-*`, `.gemini/...` generated cache trees, or files emptied by interrupted checkout unless explicitly confirmed as intended deliverables.

## Final Verification

```bash
git push origin main
git -c status.showUntrackedFiles=no status --short --branch
git rev-parse HEAD origin/main
git rev-list --left-right --count HEAD...origin/main
../scripts/repository_sync status <repo-name>
```

Expected clean result:

```text
Everything up-to-date
## main...origin/main
0    0
Changes: None
Remote: Up to date
```
