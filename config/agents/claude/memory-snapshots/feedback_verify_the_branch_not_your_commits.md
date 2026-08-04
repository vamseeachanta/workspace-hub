---
name: feedback_verify_the_branch_not_your_commits
description: "Auto-sync commits the dirty tree onto WHATEVER branch is checked out — verify the PR's own file list before opening it, and switch back to main after pushing"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 19c1569d-4a9e-4d87-bd34-50c2605be4d1
  modified: 2026-08-03T16:38:59.766Z
---

What ships is **the branch**, not the commits you made on it.

2026-08-02, workspace-hub PR #3782. I made two pathspec-scoped commits (2 files), verified the tests, pushed, opened the PR. The Client-PII Gate then failed on files I had never touched. Cause: `cf35badd5 chore(sync): auto-sync 2026-08-02` landed on my feature branch between my commit and the merge attempt, sweeping in **251 `.claude/memory/` files**, several carrying client identifiers.

"I only committed two files" was **true and insufficient**. I verified my commits and never verified the PR.

**Why:** the 4-hourly auto-sync commits whatever is dirty onto **whatever branch is currently checked out**. Leaving the shared checkout parked on a feature branch aims that sweep at your PR. This is the same daemon behind [[feedback_autosync_silent_pusher]] and the HEAD-resets-to-main behaviour — one process, several faces:

- HEAD silently returns to `main` mid-session
- `git push` reports `Everything up-to-date` on a branch you never pushed (it pushed for you)
- a sync commit appears on your feature branch carrying unrelated churn

**How to apply:**

1. **After pushing a feature branch, `git checkout main`.** This is the preventive step, not a tidiness habit — it points the sweep at main where that churn belongs. It is the single action that would have avoided this.
2. **Before opening a PR, verify the PR — not your commits:**
   ```
   gh pr view <N> --json files,commits --jq '{files:[.files[].path],commits:[.commits[].messageHeadline]}'
   ```
   Or pre-push: `git diff --name-only origin/main...HEAD`. Note the **three-dot** form — two dots against a moving `origin/main` misreports.
3. **A PII/secret gate failing on files you don't recognise means contamination, not a false positive.** Read the file list before assuming the gate is wrong. It was right.
4. **Repair is a force-push, and the agent cannot do it.** `git reset --hard` is auto-denied, and attempting it can tip the classifier into denying plain `git rev-parse` too. Hand the user the four-line sequence (checkout branch → `reset --hard <last-good>` → `push --force-with-lease --no-verify` → `checkout main`) rather than trying to route around the denial. Nothing is lost: auto-sync re-sweeps that churn onto main continuously.
5. `git revert <sync-sha>` is the non-destructive alternative when a rewrite is unwelcome — messier history, no force-push.

**Adjacent trap seen the same day:** on this `fuseblk` (NTFS-FUSE) mount, `cp .git/hooks/pre-push.sh scripts/hooks/pre-push.sh` produced an **aliased** copy — subsequent edits to the "working copy" mutated the live hook. Verify independence with `stat -c '%i %h %n' <a> <b>` before treating a copy as a scratch file, especially when the original is a live enforcement gate. See [[reference_ntfs_fuse_git_stalls_local_analysis]].

## 2026-08-03: the same daemon REVERTS MERGED WORK, under an unrelated message

Strictly worse than the sweep. `382e4a180 chore(gtm): weekly job market scan refresh` deleted **106 lines** from `scripts/enforcement/install-hooks.sh`, removing an entire change that had merged hours earlier (`9cfe69501`, PR #3783). The same commit also deleted three plan files and a plan-approval marker (`0+/137-`, `0+/101-`, `0+/89-`, `0+/41-`).

**Mechanism:** the PR merged **on GitHub** while the local working tree still held the pre-merge copy. Auto-sync committed the dirty tree, writing stale content back over the merged version.

**Why this is the dangerous variant:** sweep contamination *adds* unrelated files — visible in any PR diff. This *deletes merged code* under an unrelated commit message — invisible. It surfaced only because a test written for the removed safety property went red.

**How to apply:**
- **After any PR merges, `git pull` before doing anything else in that repo.** A merged-on-GitHub change plus a stale local tree is a pending revert waiting for the next auto-sync tick.
- **Suspect a revert when a merged feature "isn't there."** Do not assume the merge failed: `git log --oneline -3 -- <file>` and look for a later unrelated commit touching it. `git show --numstat <sha> | awk '$2>$1'` lists what a commit net-deleted.
- Restore verbatim from the merge commit: `git show <merge-sha>:<path> > <path>`.
- **This is an argument for tests over review.** Review reads a diff at one moment; a test re-asserts the property on every run. The refusal guard here caught its own removal — nothing else would have.

Related: [[feedback_multi_agent_commit_serialization]], [[feedback_retry_loop_sweep_contamination]], [[feedback_prepush_no_verify_allowed_on_feature_branch]], [[feedback_client_pii_gate_scans_commit_messages]], [[feedback_absence_of_signal_reads_as_success]].
