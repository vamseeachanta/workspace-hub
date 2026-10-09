# Ambiguous push result race

Use when `git push` exits non-zero or prints a remote ref-lock/rejection message during active multi-agent or scheduled-writer work, especially when another process may have pushed the same local commit or advanced the remote during hook execution.

## Symptom

A push may print a rejection such as:

```text
! [remote rejected] main -> main (cannot lock ref 'refs/heads/main': is at <new> but expected <old>)
error: failed to push some refs
```

But a follow-up `git ls-remote origin refs/heads/main` can show that the remote now equals local `HEAD`.

## Correct response

Do **not** immediately run `git pull`, `git rebase`, `git reset`, or cherry-pick repair just because the push command returned non-zero.

1. Capture local and remote heads:

   ```bash
   local_head=$(git rev-parse HEAD)
   remote_head=$(git ls-remote origin refs/heads/main | cut -f1)
   printf 'local=%s\nremote=%s\n' "$local_head" "$remote_head"
   ```

2. If `local_head == remote_head`, treat the durable push as successful and continue with issue/comment/label closeout.
3. If they differ, inspect divergence before repair:

   ```bash
   git fetch origin main
   git log --left-right --cherry-pick --oneline HEAD...origin/main
   ```

4. Only then choose a repair path:
   - fast-forward/absorb if local has no unique work;
   - remote-first temporary worktree + cherry-pick for narrow artifact commits;
   - stop and classify if unrelated dirty state or overlapping changes are present.

## Why

In shared checkouts, hooks, scheduled jobs, or another session may push while the current process still reports an error. The only authoritative post-push fact is the verified remote ref, not the push process exit text alone.

## Verification

Before claiming the artifact is landed:

```bash
git rev-parse HEAD
git ls-remote origin refs/heads/main | cut -f1
git status --porcelain=v1 --branch
```

Report both SHAs when relevant.
