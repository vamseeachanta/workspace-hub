# Clean duplicate clone deletion pattern — 2026-05-18

## When this applies

A top-level sibling directory under `/mnt/local-analysis` is a full git clone of a canonical repo, but exists under an ad-hoc/reconcile/staging name rather than the repo's canonical directory name.

Example pattern observed:

- Canonical repo retained: `/mnt/local-analysis/workspace-hub`
- Duplicate clone candidate: `/mnt/local-analysis/reconcile-workspace-hub-20260518-145635`
- Candidate remote: `https://github.com/vamseeachanta/workspace-hub.git`

## Verification sequence

Before offering deletion, verify all of the following:

1. Identify candidate remote, branch, HEAD, and upstream.
2. `git fetch --prune origin` in the candidate.
3. Confirm the candidate is clean:
   - `git status --short` returns no paths.
   - `git stash list` returns no entries.
4. Confirm candidate has no unique commits:
   - `git rev-list --left-right --count HEAD...@{upstream}` returns `0 N`.
   - `git branch -r --contains HEAD` includes the upstream/default branch.
5. Confirm the canonical repo remains present and is not the deletion target.
6. Run race checks for active processes/session references before deletion.
7. Ask for explicit user approval.
8. Use lock + move-to-trash-stage + remove + post-verification.

## Classification rule

If the duplicate clone is clean, stash-free, ahead by 0, and its HEAD is contained in origin history, it can be proposed as **Tier 0 — safe delete** even when it is behind origin. Being behind origin means the duplicate is stale, not valuable.

If any of these checks fail, demote to Tier 3 defer:

- dirty working tree
- untracked files that are not clearly disposable
- stashes
- ahead count > 0
- HEAD not contained in a remote branch
- remote does not match the canonical repo being compared
- active process/session references

## Closeout evidence to report

Final response should include:

- deleted paths
- explicitly deferred paths and why
- absence verification for deleted paths
- absence verification for temporary cleanup lock/trash
- before/after disk usage if collected
