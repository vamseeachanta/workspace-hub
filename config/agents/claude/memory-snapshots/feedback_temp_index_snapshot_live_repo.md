---
name: feedback_temp_index_snapshot_live_repo
description: Snapshot a live-process working tree to a branch via temp-index plumbing instead of a worktree
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 6a1ea957-75ad-490c-a8d1-8032917427d9
---

To preserve uncommitted work on `workspace-hub` (or any huge repo) while the Hermes fleet / a live session is actively using it, do NOT checkout a branch (moves HEAD out from under the fleet) and do NOT use `isolation: worktree` (33K-file materialization is too slow — see [[feedback_worktree_isolation_large_repo_cost]] / [[feedback_worktree_materialization_variance]]). Instead snapshot via plumbing against a **temp index**:

```
BASE=$(git rev-parse HEAD)
export GIT_INDEX_FILE=/tmp/recovery.index; rm -f "$GIT_INDEX_FILE"
git read-tree "$BASE"
for p in <authored paths>; do git add -- "$p"; done   # add per-path, NOT one multi-pathspec call
TREE=$(git write-tree)
COMMIT=$(git commit-tree "$TREE" -p "$BASE" -m "...")
git update-ref refs/heads/recovery/<name> "$COMMIT"
unset GIT_INDEX_FILE
git push --no-verify -u origin recovery/<name>
```

**Why:** every index-writing step targets the temp index, never `.git/index`, so it can't race the fleet's commits; HEAD and main never move; the fleet runs undisturbed. `read-tree` on a huge repo is slow (~minutes) but far faster than worktree checkout.

**How to apply:** (1) `git add -- A B C` is all-or-nothing — if ANY pathspec matches zero files it aborts and stages NOTHING; never hide this with `2>/dev/null` on a write path; add per-path in a loop. (2) Preservation pushes may use `push --no-verify` to bypass the pre-push validation gate (`0 PASS, N FAIL` / config-drift) — sanctioned by [[feedback_pre_push_hook_no_verify_for_preservation]]; the commit-time gate is still never bypassed. (3) Leave fleet-owned data (`config/ai-tools/*`, `provider-*` dashboards, `.claude/state/*`, `logs/`) out of the snapshot — the fleet re-commits it.
