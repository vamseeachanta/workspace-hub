# Archived Skill: `full-branch-cleanup-and-worktree-hygiene`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/full-branch-cleanup-and-worktree-hygiene`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/full-branch-cleanup-and-worktree-hygiene`
Consolidation date: 2026-04-29

---

---
name: full-branch-cleanup-and-worktree-hygiene
description: Track all dirty/untracked workspace-hub changes, merge stale branches into main, clean remote/local branches, and remove stale worktrees while preserving tracked nested gitlinks.
version: 1.0.0
author: Hermes Agent
tags: [git, branch-cleanup, worktree, workspace-hub, merge-hygiene]
---

# Full Branch Cleanup and Worktree Hygiene

Use when the user asks to:
- track all untracked files/changes
- merge work to origin/main
- merge all branches to `main`
- clean stale local/remote branches and worktrees

This is a high-side-effect workflow. It is appropriate only when the user explicitly authorizes broad branch cleanup.

## Core sequence

1. Start from a live inventory:
   ```bash
   git status --short --branch
   git branch -vv
   git branch -r
   git worktree list --porcelain
   git ls-remote --heads origin
   ```

2. Track dirty changes before branch deletion.
   - Commit root dirty/untracked files in a broad sync commit if the user asked to track all changes.
   - If a dirty path is itself a nested git repo/worktree/submodule, inspect it separately first.

3. Preserve nested gitlinks correctly.
   - Check whether a nested path is tracked as a gitlink:
     ```bash
     git ls-files -s <path>
     ```
   - Mode `160000` means the parent repo tracks a gitlink. Do not delete it as generic stale-worktree cleanup.
   - Commit inside the nested repo first:
     ```bash
     git -C <nested> add -A
     git -C <nested> commit -m "..."
     ```
   - Then stage/commit the parent gitlink update.

4. Merge current integration/feature branches to `main`.
   - Switch to `main` and fast-forward from origin first:
     ```bash
     git checkout main
     git pull --ff-only origin main
     ```
   - Identify branches that still contain unique commits:
     ```bash
     git rev-list --left-right --count main...<branch>
     ```
     The right-side count is `branch_only`; merge branches with `branch_only > 0`.
   - For remote-only branches, use `origin/<branch>` in the same check.

5. Resolve stale-branch conflicts conservatively.
   - For stale branches that conflict in planning indexes or duplicated artifacts, prefer current `main` for overlapping/conflicted files while accepting non-conflicting branch files:
     ```bash
     git checkout --ours -- <conflicted-file>
     git add <conflicted-file>
     git commit -m "Merge branch '<branch>' into main"
     ```
   - If a non-conflicting branch change triggers a security/content hook, drop just that file back to current `main` and record the reason in a handoff. Preserve unrelated review evidence/artifacts where safe.
   - Avoid bypassing hooks during cleanup unless explicitly approved and documented.

6. Push and verify remote state.
   - Push `main`.
   - GitHub may print `cannot lock ref ... is at <new> but expected <old>` even when the remote ref advanced. Always verify before retrying:
     ```bash
     git ls-remote --heads origin main
     git status --short --branch
     ```

7. Delete merged remote branches.
   - Only delete a remote branch if it is an ancestor of `main`:
     ```bash
     git merge-base --is-ancestor origin/<branch> main
     git push origin --delete <branch>
     ```
   - Then prune and verify:
     ```bash
     git fetch --all --prune
     git branch -r
     ```

8. Remove stale worktrees before deleting local branches.
   - Worktrees block branch deletion.
   - Remove stale worktrees with `git worktree remove -f <path>`.
   - Retain intentional tracked gitlinks/nested repos unless separately approved.
   - If there are dozens of worktrees, the removal loop may exceed tool/terminal timeouts. Treat timeout as partial progress: re-run `git worktree list --porcelain`, continue removing the remaining paths, then `git worktree prune`.
   - If `git worktree remove` reports a missing `.git` file for a stale path, run `git worktree prune` and re-check before attempting manual filesystem cleanup.
   - Run `git worktree prune` afterward.

9. Delete merged local branches.
   ```bash
   current=$(git branch --show-current)
   for b in $(git for-each-ref --format='%(refname:short)' refs/heads); do
     [ "$b" = "$current" ] && continue
     if git merge-base --is-ancestor "$b" main; then
       git branch -D "$b"
     fi
   done
   ```

10. Write a cleanup handoff and commit it.
    Include final branch/worktree state, retained gitlinks, merged branches, deleted remote branches, conflict-resolution choices, and next-session notes.

## Final verification checklist

Expected full-cleanup end-state:

```bash
git status --short --branch        # clean on main
git branch -a                      # only main + origin/main
git worktree list                  # main + intentional retained gitlinks only
git ls-remote --heads origin       # only refs/heads/main unless protected branches intentionally remain
```

Also verify no local branch has unique commits left:

```bash
python - <<'PY'
import subprocess
for b in subprocess.check_output(['git','for-each-ref','--format=%(refname:short)','refs/heads'], text=True).splitlines():
    if b == 'main':
        continue
    ahead = subprocess.check_output(['git','rev-list','--right-only','--count',f'main...{b}'], text=True).strip()
    print(b, ahead)
PY
```

## Pitfalls

- Do not remove a tracked gitlink just because `git worktree list` shows it as a detached worktree.
- Do not trust a failed-looking push if the error is `cannot lock ref`; verify with `git ls-remote`.
- Do not delete unmerged remote branches without proving ancestry into `main`.
- Do not let stale branch conflicts overwrite current planning indexes with older statuses.
- Do not normalize hook bypass during cleanup; prefer resolving or dropping the offending stale file.
- Auto-sync/background processes can create new dirty provider scorecards, planning markers, or handoffs immediately after a clean commit/push. Re-run `git status --short --branch` after every push/merge wave; if the user explicitly asked to track all changes, commit the new dirt too before declaring the checkout clean.
- Another terminal may approve an issue during cleanup, creating approval markers and plan/index updates while your handoff is being written. Before exit, revalidate live GitHub labels plus local `.planning/plan-approved/<issue>.md`, plan header, and `docs/plans/README.md`, then either commit the approval-state sync or document that it is already committed.
