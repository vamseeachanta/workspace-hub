> Git-tracked snapshot from Claude auto-memory. Captured: 2026-05-19
> Source: /home/vamsee/.claude/projects/-mnt-local-analysis-workspace-hub/memory/feedback_autostash_replay_after_checkout_b.md

---
name: autostash-replay-after-checkout-b
description: "When `git checkout -b` runs with a leftover autostash in `git stash list`, the stash can auto-apply to the new branch and silently revert tracked state. Always `git stash list` and drop unwanted autostashes BEFORE creating new branches, especially after operations like `git rebase --onto` that produce autostashes."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 76ab2ab3-ba1e-4c05-b984-b73d97dafefc
---

Before running `git checkout -b <new-branch>` or `git switch -c <new-branch>`, run `git stash list`. If `stash@{0}` is `autostash` (no descriptive message), DROP it explicitly with `git stash drop stash@{0}` before creating the branch. Otherwise the autostash can replay onto the new branch and silently corrupt the working tree + index.

**Why:** On 2026-05-14, after a clean `git rebase --onto 87b792c1b 98b318b4e issue-2703-skill-curation` (which dropped a self-approval marker commit), an autostash `4572639b8` was left in `stash@{0}`. Later, `git checkout -b feat/marker-label-parity-gate` from main HEAD `5a93fe45c` triggered the autostash to replay — git's message was "Autostash exists; creating a new stash entry", which is technically correct but easy to miss. The replay applied OLD content (pre-merge-of-#2705 state) onto the new branch's working tree + index. The next commit (`51887c839`) captured: deletes of the 4 PR-#2705-merged files, reverse-renames of 2 SKILL files (hyphen back to underscore), AND my legitimate 2 intended files. Recovery cost ~10 turns: defensive backup of intended files to `/tmp`, hard reset to `5a93fe45c`, restoration from `/tmp`, narrow re-commit. Recovered cleanly via `feedback_reflog_as_ground_truth` discipline.

The closest existing memory entries cover related but distinct patterns: [[feedback_retry_loop_reset_hazard]] is about `git reset HEAD -- .` in retry loops; [[feedback_autosync_silent_pusher]] is about silent pushes; this one is uniquely about autostash apply during branch creation.

**How to apply:**

1. After ANY `git rebase`, `git pull --rebase`, or `git checkout` that may have triggered autostash:
   ```
   git stash list | head -3
   ```
2. If `stash@{0}: autostash` is present and the work it would protect has already landed (committed to the target branch), drop it:
   ```
   git stash drop stash@{0}
   ```
3. Only THEN create new branches: `git checkout -b <name>` or `git switch -c <name>`.
4. Audit the first commit on a fresh branch with `git show --stat HEAD` BEFORE pushing — if it touches files outside what your `git add` named, suspect autostash replay and recover via `git reset --hard <correct-base>` + restore-from-/tmp pattern.
5. The `--no-autostash` flag on `git pull --rebase` (and `pull.rebase = true` configs) prevents autostash creation in the first place; consider for rebase-heavy workflows.
